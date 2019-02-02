package main

import (
	"sort"
	"fmt"
	"log"
	"time"
	"comm"
	"net"
	"os"
	"io"
	"bufio"
	"os/signal"
	// "syscall"
	"io/ioutil"
	"strings"
	"strconv"
	"encoding/json"
	"math/rand"
)

const FS_thresh float32 = 1793.5
const Spider_path_cnt int = 4
const Flash_path_cnt int = 10

// global vars
var nd	Comm.Node
// configuration
var node_conf Comm.NodeInfo
var neig_conf Comm.NeigConf
// paths processed offline
var P map[int][]Comm.Path
//
var is_active bool = true
// for test
var g_nodeid int
var g_algo int
var G[Comm.G_SIZE+1][Comm.G_SIZE+1] float32
var bk_G[Comm.G_SIZE+1][Comm.G_SIZE+1] float32
var all_trans []Comm.Trans
var trans_ch chan Comm.Msg

func pr_G(graph [Comm.G_SIZE+1][Comm.G_SIZE+1] float32) {
	for i:=0; i<=Comm.G_SIZE; i++ {
		for j:=0; j<=Comm.G_SIZE; j++ {
			fmt.Printf("%.2f ", graph[i][j])
		}
		fmt.Println()
	}
}

func init_G(g_filename string) bool {
	var ret bool = true
	for i:=0; i<=Comm.G_SIZE; i++ {
		for j:=0; j<=Comm.G_SIZE; j++ {
			G[i][j] = Comm.PATH_NOT_PROBED;
		}
	}

	file, err := os.Open(g_filename)
	if err != nil {
		ret = false
		log.Println("error reading graph file", err)
		return ret
	}
	defer file.Close()
	br := bufio.NewReader(file)

	for {
		line, _, err := br.ReadLine()
		if err == io.EOF {
			break;
		}
		// split by ','
		lines := strings.Split(string(line), ",")
		if 3 != len(lines) {
			log.Println("bad format in graph file qnmlgb")
			ret = false
			break
		}
		src, _ := strconv.Atoi(lines[0])
		src += 1
		dst, _ := strconv.Atoi(lines[1])
		dst += 1
		_, _ = strconv.ParseFloat(lines[2], 32) // capacity not used here

		G[src][dst] = Comm.PATH_INITED
	}

	bk_G = G

	return ret
}

func load_trans(trans_filename string) bool {
	var ret bool = true // true --> successful
	var trans Comm.Trans
	file, err := os.Open(trans_filename)
	if err != nil {
		ret = false
		log.Println("error reading trans file", err)
		return ret
	}

	defer file.Close()
	br := bufio.NewReader(file)

	for {
		line, _, err := br.ReadLine()
		if err == io.EOF {
			break;
		}
		// split by ','
		lines := strings.Split(string(line), ",")
		if 3 != len(lines) {
			log.Println("bad format in trans file qnmlgb")
			ret = false
			break
		}
		trans.Src, _ = strconv.Atoi(lines[0])
		trans.Dst, _ = strconv.Atoi(lines[1])
		tmp_float32, _ := strconv.ParseFloat(lines[2], 32)
		trans.Volume = float32(tmp_float32)

		all_trans = append(all_trans, trans)
	}

	// for test
	/*
	for _, tr := range all_trans {
		log.Printf("%d %d %f\n", tr.Src, tr.Dst, tr.Volume)
	}*/


	return ret
	
}

func load_paths (paths_filename string) bool {
	P = make(map[int][]Comm.Path)
	var ret bool = true // true --> successful
	file, err := os.Open(paths_filename)
	if err != nil {
		ret = false
		log.Println("error reading trans file", err)
		return ret
	}

	defer file.Close()
	br := bufio.NewReader(file)

	for {
		var path Comm.Path
		line, _, err := br.ReadLine()
		if err == io.EOF {
			break;
		}
		// split by ','
		lines := strings.Split(string(line), ",")
		if 2 > len(lines) {
			log.Println("bad format in trans file qnmlgb")
			ret = false
			break
		}

		dst_id, _ := strconv.Atoi(lines[0])
		for i:=1; i<len(lines); i++ {
			node_id, _ := strconv.Atoi(lines[i])
			path.Nid = append(path.Nid, node_id)
		}

		P[dst_id] = append(P[dst_id], path)
	}

	var path_needed int = 0
	if g_algo == 0 {
		path_needed = Flash_path_cnt
	} else if g_algo == 2 {
		path_needed = Spider_path_cnt
	}
	for k, _ := range P {
		if len(P[k]) > path_needed {
			P[k] = P[k][:path_needed]
		}
	}
	fmt.Println("path loaded")

	// for test
	/*
	for k, v := range P {
		fmt.Printf("to dst %d\n", k)
		for _, node_id := range v {
			fmt.Printf("%d ", node_id)
		}
		fmt.Printf("\n")
	}*/

	return ret
}


func handle_sig() {
	for is_active {
		c := make(chan os.Signal)
		signal.Notify(c)
		// s := <-c
		<-c
		is_active = false
		// panic("Want stack trace")
		os.Exit(-1)
	}
}
//
func fwdmsg_SessOut_by_nid(msg *Comm.Msg, nid int) {
	for i, ses := range nd.Sess_out {
		if ses.NI.NodeID == nid {
			// fmt.Println(len(nd.Sess_out[i].Msg_ch))
			nd.Sess_out[i].Msg_ch <- *msg
			break;
		}
	}
}

// spider algo
func Spider (paths []Comm.Potential_path, demand float32) bool {
	var is_satisfied bool = false
	var tot_capacity float32 = 0
	for i:=0; i<len(paths); i++ {
		tot_capacity += paths[i].Capacity
		// initialize
		paths[i].ActCommit = 0
	}
	if tot_capacity < demand {
		return is_satisfied
	}

	is_satisfied = true
	// sort
	sort.Slice(paths, func(i, j int) bool {
		return paths[i].Capacity > paths[j].Capacity
	})
	var remain_vol float32 = demand
	var commit_vol float32
	for remain_vol > 0 {
		/*
		fmt.Println("here???", remain_vol)
		var test int
		fmt.Scanln(&test)*/
		var largest float32 = paths[0].Capacity
		var seclargest float32
		var set_largest []Comm.Potential_path
		for ind:=0; ind < len(paths); ind++ {
			if paths[ind].Capacity == largest {
				set_largest = append(set_largest, paths[ind])
			} else {
				seclargest = paths[ind].Capacity
				break
			}
		}

		diff := largest - seclargest
		if float32(len(set_largest)) * diff > remain_vol {
			commit_vol = float32(remain_vol)/float32(len(set_largest))
			remain_vol = 0
		} else {
			commit_vol = diff
			remain_vol -= diff * float32(len(set_largest))
		}

		for ind:=0; ind<len(set_largest); ind++ {
			paths[ind].Capacity -= commit_vol
			paths[ind].ActCommit += commit_vol
		}
	}
	
	// for test
	/*
	for ind:=0; ind<len(paths); ind++ {
		fmt.Println(paths[ind].Capacity, paths[ind].ActCommit)
	}*/

	return is_satisfied
}

// spider handle
func Spider_HandleTrans () {
	/* a brief intro to progress
		1) offline find route
		2) probe each route
		3) run spider algo
		4) if can not satisfy, fail
		5) if can, commit each path
		6) if all paths pass, success
		if not successful
			reverse previous all commit
		if successful
			do nothing
	*/
	trans_ch = make(chan Comm.Msg, 1000)
	// trans_ch = make(chan Comm.Msg)
	var committed_msg []Comm.Msg 
	var num_succ int = 0
	var num_fail int = 0
	var succ_volume float64 = 0
	var t_shortflow float64 = 0
	var t_largeflow float64 = 0
	var n_short int = 0
	var n_large int = 0
	var n_large_succ int = 0
	time.Sleep(5*time.Second)

	for i, tr := range all_trans {
		t_st := time.Now()
		// handle each transaction
		var fwd_msg Comm.Msg
		var recv_msg Comm.Msg
		var trans_succ_flag bool = true
		var is_short_flow bool = false
		if tr.Volume <= FS_thresh {
			is_short_flow = true
			n_short += 1
		} else {
			is_short_flow = false
			n_large += 1
		}

		var p_paths []Comm.Potential_path
		for _, s_path := range P[tr.Dst] {
			var p_path Comm.Potential_path
			p_path.ActCommit = 0
			p_path.Capacity = -1
			p_path.Nid = s_path.Nid

			p_paths = append(p_paths, p_path)
		}

		// probe
		for ind, s_path := range p_paths {
			fwd_msg.Type = Comm.MSG_TYPE_PROBE
			fwd_msg.TransID = 1000*g_nodeid+i
			fwd_msg.ReqID = ind
			fwd_msg.Src = tr.Src
			fwd_msg.Dst = tr.Dst
			fwd_msg.Path = s_path.Nid

			fwdmsg_SessOut_by_nid(&fwd_msg, fwd_msg.Path[1])
			// fmt.Println("probe sent", fwd_msg.Path)

			// probe ret and update graph
			recv_msg = <- trans_ch
			// fmt.Println("probe ret received")
			var vol_commit float32 = -1
			for i:=0; i<=len(recv_msg.Path)-2; i++ {
				G[recv_msg.Path[i]][recv_msg.Path[i+1]] = recv_msg.Cap[i]
				if vol_commit<0 || (recv_msg.Cap[i]<vol_commit && vol_commit>0) {
					vol_commit = recv_msg.Cap[i]
				}
			}
			if vol_commit <= 0 {
				vol_commit = 0
			}

			p_paths[ind].Capacity = vol_commit
		}

		if Spider(p_paths, tr.Volume) == false {
			trans_succ_flag = false
		}
		// commit 
		if trans_succ_flag == true {
			for _, s_path := range p_paths {
				if s_path.ActCommit > 0 {
					fwd_msg.Type = Comm.MSG_TYPE_COMMIT
					fwd_msg.Src = tr.Src
					fwd_msg.Dst = tr.Dst
					fwd_msg.Path = s_path.Nid
					fwd_msg.Cap = nil
					fwd_msg.P1c = nil
					fwd_msg.Commit = s_path.ActCommit
					fwd_msg.ActCommit = -1

					fwdmsg_SessOut_by_nid(&fwd_msg, fwd_msg.Path[1])
					// fmt.Println("commit sent")
					//  commit ret and update graph
					recv_msg = <- trans_ch
					// fmt.Println("commit ret received")

					committed_msg = append(committed_msg, recv_msg)
					if recv_msg.ActCommit < s_path.ActCommit {
						// fmt.Printf("need %.3f, act %.3f\n", s_path.ActCommit, recv_msg.ActCommit)
						trans_succ_flag = false
						break
					}
				}
			}
		}
		// clear graph and proceed next
		G = bk_G
		if trans_succ_flag == false {
			// reverse all the committed
			for _, c_msg := range committed_msg {
				c_msg.Type = Comm.MSG_TYPE_REVERSE
				c_msg.Reverse = c_msg.ActCommit
				// log.Println(c_msg)
				fwdmsg_SessOut_by_nid(&c_msg, c_msg.Path[1])
				// fmt.Println("fail reverse sent")
				_ = <- trans_ch
				// fmt.Println("fail reverse ret received")
			}
			num_fail += 1
		} else {
			// confirm all the committed
			for _, c_msg := range committed_msg {
				c_msg.Type = Comm.MSG_TYPE_CONFIRM
				fwdmsg_SessOut_by_nid(&c_msg, c_msg.Path[1])
				// fmt.Println("success commit sent")
				_ = <- trans_ch
				// fmt.Println("success commit ret received")
			}
			num_succ += 1
			succ_volume += float64(tr.Volume)
		}

		fmt.Printf("processed[%d]/[%d]\n", i+1, len(all_trans))
		t_ed := time.Now()
		t_elapsed := t_ed.Sub(t_st)
		if is_short_flow == true {
			t_shortflow += float64(t_elapsed)/float64(time.Millisecond)
		} else {
			if trans_succ_flag == true {
				t_largeflow += float64(t_elapsed)/float64(time.Millisecond)
				n_large_succ += 1
			}
		}

		committed_msg = committed_msg[0:0]
	}

	// fmt.Fprintf(os.Stderr, "%f %d %d\n", float64(t_elapsed.Nanoseconds()/1e3), num_succ, num_fail)
	time.Sleep(20*time.Second)
	var sum_N_msg_probe int = 0
	var sum_N_msg_commit int = 0
	var sum_N_msg_reverse int = 0
	var sum_N_msg_confirm int = 0
	for ind, _ := range nd.Sess_out {
		sum_N_msg_probe += nd.Sess_out[ind].N_msg_probe
		sum_N_msg_commit += nd.Sess_out[ind].N_msg_commit
		sum_N_msg_reverse += nd.Sess_out[ind].N_msg_reverse
		sum_N_msg_confirm += nd.Sess_out[ind].N_msg_confirm
	}
	fmt.Printf("finished %f %f %f %d %d %f %d %d %d %d\n", t_shortflow/float64(n_short), t_largeflow/float64(n_large_succ), 
	(t_shortflow+t_largeflow)/float64(num_succ+num_fail+n_large_succ-n_large), 
	num_succ, num_fail, succ_volume, 
	sum_N_msg_probe, sum_N_msg_commit, sum_N_msg_reverse, sum_N_msg_confirm)
	// log.Printf("#succ [%d]\t#fail [%d]\n", num_succ, num_fail)
}

// shortest_path handle
func SP_HandleTrans () {
	/* a brief intro to progress
		1) bfs to find route
		2) commit
		3) receive how much commited
		if not successful
			reverse previous all commit
		if successful
			do nothing
	*/
	trans_ch = make(chan Comm.Msg, 1000)
	// trans_ch = make(chan Comm.Msg)
	var committed_msg []Comm.Msg 
	var num_succ int = 0
	var num_fail int = 0
	var succ_volume float64 = 0
	var t_shortflow float64 = 0
	var t_largeflow float64 = 0
	var n_short int = 0
	var n_large int = 0
	time.Sleep(5*time.Second)

	for i, tr := range all_trans {
		t_st := time.Now()
		// handle each transaction
		var fwd_msg Comm.Msg
		var recv_msg Comm.Msg
		var trans_succ_flag bool = false
		var num_probe int = 1
		var is_short_flow bool = false
		if tr.Volume <= FS_thresh {
			is_short_flow = true
			n_short += 1
		} else {
			is_short_flow = false
			n_large += 1
		}
		for num_probe > 0 {
			num_probe -= 1
			path, if_found := Comm.Bfs_shortest_path(&G, tr.Src, tr.Dst, Comm.G_SIZE)
			if if_found == false {
				// no more path
				break
			}


			// commit 
			fwd_msg.Type = Comm.MSG_TYPE_COMMIT
			fwd_msg.TransID = 1000*g_nodeid+i
			fwd_msg.ReqID = num_probe
			fwd_msg.Src = tr.Src
			fwd_msg.Dst = tr.Dst
			// fwd_msg.Path = path[0] // only 1 path here
			fwd_msg.Path = path // only 1 path here

			fwd_msg.Commit = tr.Volume
			fwd_msg.ActCommit = -1

			fwdmsg_SessOut_by_nid(&fwd_msg, fwd_msg.Path[1])
			// fmt.Println("commit sent")
			//  commit ret and update graph
			recv_msg = <- trans_ch
			// fmt.Println("commit ret received")
			// log.Println("Trans:", recv_msg)
			if recv_msg.ActCommit >= tr.Volume {
				trans_succ_flag = true
				break;
			}

			committed_msg = append(committed_msg, recv_msg)
		}
		// clear graph and proceed next
		G = bk_G
		if trans_succ_flag == false {
			// reverse all the committed
			for _, c_msg := range committed_msg {
				c_msg.Type = Comm.MSG_TYPE_REVERSE
				c_msg.Reverse = c_msg.ActCommit
				// log.Println(c_msg)
				fwdmsg_SessOut_by_nid(&c_msg, c_msg.Path[1])
				// fmt.Println("fail reverse sent")
				_ = <- trans_ch
				// fmt.Println("fail reverse ret received")
			}
			num_fail += 1
		} else {
			// confirm all the committed
			for _, c_msg := range committed_msg {
				c_msg.Type = Comm.MSG_TYPE_CONFIRM
				fwdmsg_SessOut_by_nid(&c_msg, c_msg.Path[1])
				// fmt.Println("success commit sent")
				_ = <- trans_ch
				// fmt.Println("success commit ret received")
			}
			num_succ += 1
			succ_volume += float64(tr.Volume)
		}

		fmt.Printf("processed[%d]/[%d]\n", i+1, len(all_trans))
		t_ed := time.Now()
		t_elapsed := t_ed.Sub(t_st)

		if is_short_flow == true {
			t_shortflow += float64(t_elapsed)/float64(time.Millisecond)
		} else {
			t_largeflow += float64(t_elapsed)/float64(time.Millisecond)
		}

		committed_msg = committed_msg[0:0]
	}

	// fmt.Fprintf(os.Stderr, "%f %d %d\n", float64(t_elapsed.Nanoseconds()/1e3), num_succ, num_fail)
	// fmt.Printf("finished %f %d %d\n", float64(t_elapsed)/float64(time.Millisecond), num_succ, num_fail)
	time.Sleep(20*time.Second)
	var sum_N_msg_probe int = 0
	var sum_N_msg_commit int = 0
	var sum_N_msg_reverse int = 0
	var sum_N_msg_confirm int = 0
	for ind, _ := range nd.Sess_out {
		sum_N_msg_probe += nd.Sess_out[ind].N_msg_probe
		sum_N_msg_commit += nd.Sess_out[ind].N_msg_commit
		sum_N_msg_reverse += nd.Sess_out[ind].N_msg_reverse
		sum_N_msg_confirm += nd.Sess_out[ind].N_msg_confirm
	}
	fmt.Printf("finished %f %f %f %d %d %f %d %d %d %d\n", t_shortflow/float64(n_short), t_largeflow/float64(n_large), 
	(t_shortflow+t_largeflow)/float64(num_succ+num_fail), 
	num_succ, num_fail, succ_volume, 
	sum_N_msg_probe, sum_N_msg_commit, sum_N_msg_reverse, sum_N_msg_confirm)
	// log.Printf("#succ [%d]\t#fail [%d]\n", num_succ, num_fail)
}

// thread for handling transactions
func HandleTrans () {
	/* a brief intro to progress
		while (trans fulfilled || #probetimes || no route)
			1) bfs to find route
			2) probe route capacity
			3) update graph 
			4) commit
			5) receive how much commited and update graph
		if not successful
			reverse previous all commit
		if successful
			do nothing
	*/
	trans_ch = make(chan Comm.Msg, 1000)
	// trans_ch = make(chan Comm.Msg)
	var committed_msg []Comm.Msg 
	var num_succ int = 0
	var num_fail int = 0
	var succ_volume float64 = 0
	var t_shortflow float64 = 0
	var t_largeflow float64 = 0
	var n_large_succ int = 0
	var n_short int = 0
	var n_large int = 0
	time.Sleep(5*time.Second)

	for i, tr := range all_trans {
		t_st := time.Now()
		// handle each transaction
		var num_probe int 
		var fwd_msg Comm.Msg
		var recv_msg Comm.Msg
		var vol_commit float32
		var remain_vol float32 = tr.Volume
		var trans_succ_flag bool = false
		var rev_amount float32 = -1
		var is_short_flow bool = false
		if tr.Volume <= FS_thresh {
			num_probe = 4
			is_short_flow = true
			n_short += 1
		} else {
			num_probe = 20
			is_short_flow = false
			n_large += 1
		}
		if is_short_flow == false {
			for {
				if remain_vol <= 0 {
					trans_succ_flag = true
					break
				}
				num_probe = num_probe - 1
				if (num_probe < 0) {
					break
				}

				path, if_found := Comm.Bfs_shortest_path(&G, tr.Src, tr.Dst, Comm.G_SIZE)
				if if_found == false {
					// no more path
					// fmt.Println("no more path", 200-num_probe)
					break
				}


				// probe
				fwd_msg.Type = Comm.MSG_TYPE_PROBE
				fwd_msg.TransID = 1000*g_nodeid+i
				fwd_msg.ReqID = num_probe
				fwd_msg.Src = tr.Src
				fwd_msg.Dst = tr.Dst
				// fwd_msg.Path = path[0] // only 1 path here
				fwd_msg.Path = path // only 1 path here

				fwdmsg_SessOut_by_nid(&fwd_msg, fwd_msg.Path[1])
				// fmt.Println("probe sent", fwd_msg.Path)

				// probe ret and update graph
				recv_msg = <- trans_ch
				// fmt.Println("probe ret received")
				vol_commit = -1
				for i:=0; i<=len(recv_msg.Path)-2; i++ {
					G[recv_msg.Path[i]][recv_msg.Path[i+1]] = recv_msg.Cap[i]
					if vol_commit<0 || (recv_msg.Cap[i]<vol_commit && vol_commit>0) {
						vol_commit = recv_msg.Cap[i]
					}
				}
				if vol_commit <= 0 {
					if vol_commit < 0 {
						fmt.Println("probed negative capacity!!!", recv_msg.Cap)
					}
					continue
				}

				if vol_commit > remain_vol {
					vol_commit = remain_vol
				}
				

				// commit 
				fwd_msg.Type = Comm.MSG_TYPE_COMMIT
				fwd_msg.Commit = vol_commit
				fwd_msg.ActCommit = -1

				fwdmsg_SessOut_by_nid(&fwd_msg, fwd_msg.Path[1])
				// fmt.Println("commit sent", fwd_msg)
				//  commit ret and update graph
				recv_msg = <- trans_ch
				// fmt.Println("commit ret received", recv_msg)
				rev_amount = 0
				// log.Println("Trans:", recv_msg)
				if recv_msg.ActCommit > 0 {
					if remain_vol < recv_msg.ActCommit {
						rev_amount = recv_msg.ActCommit-remain_vol
						remain_vol = 0
					} else {
						remain_vol -= recv_msg.ActCommit
					}
					for i:=0; i<=len(recv_msg.Path)-2; i++ {
						G[recv_msg.Path[i]][recv_msg.Path[i+1]] -= recv_msg.ActCommit
						G[recv_msg.Path[i]][recv_msg.Path[i+1]] += rev_amount
					}
				}

				// need reverse?
				if rev_amount > 0 {
					fwd_msg.ActCommit -= rev_amount
					fwd_msg.Type = Comm.MSG_TYPE_REVERSE
					fwd_msg.Reverse = rev_amount
					fwdmsg_SessOut_by_nid(&fwd_msg, fwd_msg.Path[1])
					// fmt.Println("reverse sent")
					_ = <- trans_ch
					// fmt.Println("reverse ret received")
				}

				committed_msg = append(committed_msg, recv_msg)
			}
		} else if is_short_flow == true {
			var n_path_probed int = 0
			var n_path int = len(P[tr.Dst])
			var path_visited[Flash_path_cnt] bool
			for p_i:=0; p_i<n_path; p_i++ {
				path_visited[p_i] = false
			}
			for {
				if remain_vol <= 0 {
					trans_succ_flag = true
					break
				}

				n_path_probed += 1

				if n_path_probed>=Spider_path_cnt || n_path_probed>=n_path {
					break
				}

				// find one path
				p_ind := rand.Intn(n_path)
				for path_visited[p_ind]==true {
					p_ind += 1
					p_ind %= n_path
				}
				path_visited[p_ind] = true
				//
				fwd_msg.Type = Comm.MSG_TYPE_COMMIT
				fwd_msg.TransID = 1000*g_nodeid+i
				fwd_msg.ReqID = p_ind // indicate which cached route
				fwd_msg.Src = tr.Src
				fwd_msg.Dst = tr.Dst
				fwd_msg.Path = P[tr.Dst][p_ind].Nid
				fwd_msg.Commit = remain_vol
				fwd_msg.ActCommit = -1

				fwdmsg_SessOut_by_nid(&fwd_msg, fwd_msg.Path[1])
				// fmt.Println("commit sent", fwd_msg)
				//  commit ret and update the remain_vol
				recv_msg = <- trans_ch
				// fmt.Println("commit ret received", recv_msg)

				remain_vol -= recv_msg.ActCommit
				
				committed_msg = append(committed_msg, recv_msg)
			}
		} else {
			fmt.Println("fatal error!")
			os.Exit(-1)
		}
		// clear graph and proceed next
		G = bk_G
		if trans_succ_flag == false {
			// reverse all the committed
			for _, c_msg := range committed_msg {
				c_msg.Type = Comm.MSG_TYPE_REVERSE
				c_msg.Reverse = c_msg.ActCommit
				// log.Println(c_msg)
				fwdmsg_SessOut_by_nid(&c_msg, c_msg.Path[1])
				// fmt.Println("fail reverse sent")
				_ = <- trans_ch
				// fmt.Println("fail reverse ret received")
			}
			num_fail += 1
		} else {
			// confirm all the committed
			for _, c_msg := range committed_msg {
				c_msg.Type = Comm.MSG_TYPE_CONFIRM
				fwdmsg_SessOut_by_nid(&c_msg, c_msg.Path[1])
				// fmt.Println("success commit sent")
				_ = <- trans_ch
				// fmt.Println("success commit ret received")
			}
			num_succ += 1
			succ_volume += float64(tr.Volume)
		}

		fmt.Printf("processed[%d]/[%d]\n", i+1, len(all_trans))
		t_ed := time.Now()
		t_elapsed := t_ed.Sub(t_st)
		if is_short_flow == true {
			t_shortflow += float64(t_elapsed)/float64(time.Millisecond)
		} else {
			if trans_succ_flag == true {
				t_largeflow += float64(t_elapsed)/float64(time.Millisecond)
				n_large_succ += 1
			}
		}

		committed_msg = committed_msg[0:0]
	}

	// fmt.Fprintf(os.Stderr, "%f %d %d\n", float64(t_elapsed.Nanoseconds()/1e3), num_succ, num_fail)
	time.Sleep(20*time.Second)
	var sum_N_msg_probe int = 0
	var sum_N_msg_commit int = 0
	var sum_N_msg_reverse int = 0
	var sum_N_msg_confirm int = 0
	for ind, _ := range nd.Sess_out {
		sum_N_msg_probe += nd.Sess_out[ind].N_msg_probe
		sum_N_msg_commit += nd.Sess_out[ind].N_msg_commit
		sum_N_msg_reverse += nd.Sess_out[ind].N_msg_reverse
		sum_N_msg_confirm += nd.Sess_out[ind].N_msg_confirm
	}
	fmt.Printf("finished %f %f %f %d %d %f %d %d %d %d\n", t_shortflow/float64(n_short), t_largeflow/float64(n_large_succ), 
	(t_shortflow+t_largeflow)/float64(num_succ+num_fail+n_large_succ-n_large), 
	num_succ, num_fail, succ_volume, 
	sum_N_msg_probe, sum_N_msg_commit, sum_N_msg_reverse, sum_N_msg_confirm)
	// log.Printf("#succ [%d]\t#fail [%d]\n", num_succ, num_fail)
}


func HandleSesOut (ses *Comm.Session) {
	// log.Printf("i am SessOut [%d] handler\n", ses.NI.NodeID)
	// TODO: need close conn?
	for msg := range ses.Msg_ch {
		// log.Printf("[OUT]handle [%d] out msg\n", ses.NI.NodeID)
		// log.Println(msg)

		// do something here
		// fmt.Println("try to lock")
		ses.CapLock.Lock()
		if msg.Type == Comm.MSG_TYPE_PROBE {
			ses.N_msg_probe += 1
			// append capacity
			msg.Cap = append(msg.Cap, ses.Cap)
		} else if msg.Type == Comm.MSG_TYPE_PROBE_RET {
			// do nothing
			// log.Printf("[OUT]received PROBE_RET %v\n", msg)
		} else if msg.Type == Comm.MSG_TYPE_COMMIT {
			ses.N_msg_commit += 1
			// check commit 
			var sesCommit float32 = 0
			if msg.ActCommit >= 0 {
				if msg.ActCommit <= ses.Cap {
					sesCommit = msg.ActCommit
					ses.Cap = ses.Cap-sesCommit
					if ses.Cap < 0 {
						fmt.Printf("ccc, 1\n")
					}
				} else if ses.Cap > 0 {
					sesCommit = ses.Cap
					ses.Cap = 0
				} else {
					sesCommit = 0
				}
				msg.P1c = append(msg.P1c, sesCommit)
				// update msg.ActCommit to the smaller one
				if msg.ActCommit>sesCommit {
					msg.ActCommit = sesCommit
				}
			} else {
				if msg.Commit >= ses.Cap {
					msg.ActCommit = ses.Cap
					ses.Cap = 0
				} else {
					msg.ActCommit = msg.Commit
					ses.Cap -= msg.Commit
				}
				msg.P1c = append(msg.P1c, msg.ActCommit)
			}
		} else if msg.Type == Comm.MSG_TYPE_COMMIT_RET {
			// we handle reverse_cap (ActCommit v.s.) in in_Session
			// we need to increase some cap here, right?

			/* do nothing
			if node_conf.NodeID == msg.Src {
			} else {
				// log.Printf("[OUT]COMMIT_RET msg to node[%d]\n", ses.NI.NodeID)
				// log.Printf("before cap[%f]\n",ses.Cap)
				ses.Cap = ses.Cap+msg.ActCommit
				// log.Printf("after cap[%f]\n",ses.Cap)
				if ses.Cap < 0 {
					fmt.Printf("ccc, 2\n")
				}
			}*/
		} else if msg.Type == Comm.MSG_TYPE_REVERSE {
			ses.N_msg_reverse += 1
			// just update the Cap
			// log.Printf("[OUT]we handle reverse msg to node[%d]\n", ses.NI.NodeID)
			// log.Printf("before cap[%f]\n",ses.Cap)
			ses.Cap = ses.Cap+msg.Reverse
				if ses.Cap < 0 {
					fmt.Printf("ccc, 3\n")
				}
			// log.Printf("after cap[%f]\n",ses.Cap)
		} else if msg.Type == Comm.MSG_TYPE_REVERSE_RET {
			// just update the Cap
			// log.Printf("[OUT]REVERSE_RET msg to node[%d]\n", ses.NI.NodeID)
			// log.Printf("before cap[%f]\n",ses.Cap)
			// do nothing
			/*
			ses.Cap = ses.Cap-msg.Reverse
				if ses.Cap < 0 {
					fmt.Println(msg)
					fmt.Printf("ccc, 4 %.3f %.3f\n", ses.Cap, msg.Reverse)
				}*/
			// log.Printf("after cap[%f]\n",ses.Cap)
		} else if msg.Type == Comm.MSG_TYPE_CONFIRM {
			// do nothing
			ses.N_msg_confirm += 1
		} else if msg.Type == Comm.MSG_TYPE_CONFIRM_RET {
			// just update the Cap
			ses.Cap = ses.Cap+msg.ActCommit
		} else {
			log.Printf("[OUT to [%d]] wtf ????\n", ses.NI.NodeID)
		}
		ses.CapLock.Unlock()
		// fmt.Println("lock released")

		// marshal and send
		b, err := json.Marshal(msg)
		if err != nil {
			log.Println("[OUT]error HandleSesOut Json Marshal", err)
			continue
		}
		// send over network
		wr_len, err := ses.Conn.Write(b)
		if err!=nil || wr_len!=len(b) {
			log.Println("[OUT]error HandleSesOut send data", err)
			ses.Conn.Close()
			break;
		}
		// log.Println("data sent", len(b))
	}
}

func updateSesOutCap (msg *Comm.Msg, prev_nodeid int, updt_ind int) {
	var test_found_flag = false

	// log.Println("", prev_nodeid, updt_ind)
	for i, _ := range nd.Sess_out {
		if nd.Sess_out[i].NI.NodeID == prev_nodeid {
			test_found_flag = true
			// fmt.Println("upt try to lock")
			nd.Sess_out[i].CapLock.Lock()
			// log.Printf("before ToNode[%d] Cap %f\n", prev_nodeid, nd.Sess_out[i].Cap)
			nd.Sess_out[i].Cap = nd.Sess_out[i].Cap+msg.P1c[updt_ind]-msg.ActCommit
			if nd.Sess_out[i].Cap < 0 {
				fmt.Println(*msg)
				fmt.Printf("ToNode[%d] %.3f Cap %.3f\n", prev_nodeid, msg.P1c[updt_ind], nd.Sess_out[i].Cap)
			}
			nd.Sess_out[i].CapLock.Unlock()
			// fmt.Println("upt lock released")
			break;
		}
	}

	if test_found_flag == false {
		log.Println("update sess out capacity error!!!")
	}
}

func HandleSesIn (conn *net.TCPConn) {
	// log.Printf("SessIn handler")
	// TODO: need close conn?
	data := make([]byte, 10240)
	for {
		rd_len, err := conn.Read(data)
		if err != nil {
			log.Println("[IN] error HandleSesIn receive data", err)
			conn.Close()
			break;
		}

		j_dec := json.NewDecoder(strings.NewReader(string(data[:rd_len])))
		for {

			var json_msg Comm.Msg
			/*
			err = json.Unmarshal(data[:rd_len], &json_msg)
			if err != nil {
				log.Println("[IN] error HandleSesIn json unmarshal", err)
				log.Println("data_len", rd_len)
				log.Println(string(data[:rd_len]))
				continue;
			}*/
			if err = j_dec.Decode(&json_msg); err == io.EOF {
				break
			} else if err != nil {
				log.Println("[IN] error json", err, rd_len)
				break
			}
			// log.Printf("[IN] handle %d msg %v\n", json_msg.Type, json_msg)


			// handle MSG in
			var next_hopNid int = -1
			var prev_hopNid int = -1
			var updt_cap_ind int = -1
			var need_forward bool = false
			var test_found_flag bool = false
			if node_conf.NodeID==json_msg.Dst {
				// 1.a) if last node
				need_forward = true
				next_hopNid = json_msg.Path[len(json_msg.Path)-2]
				if json_msg.Type==Comm.MSG_TYPE_PROBE {
					json_msg.Type = Comm.MSG_TYPE_PROBE_RET
				} else if json_msg.Type==Comm.MSG_TYPE_COMMIT {
					json_msg.Type = Comm.MSG_TYPE_COMMIT_RET
				} else if json_msg.Type==Comm.MSG_TYPE_REVERSE {
					json_msg.Type = Comm.MSG_TYPE_REVERSE_RET
				} else if json_msg.Type==Comm.MSG_TYPE_CONFIRM {
					json_msg.Type = Comm.MSG_TYPE_CONFIRM_RET
				} else {
					// err
					log.Println("error, supposed to be PROBE or COMMIT")
				}
			} else if node_conf.NodeID==json_msg.Src {
				// 1.b) if last node
				if json_msg.Type==Comm.MSG_TYPE_PROBE_RET {
					// TODO: construct weighted Map
					trans_ch <- json_msg
				} else if json_msg.Type==Comm.MSG_TYPE_COMMIT_RET {
					// TODO: next route???
					// log.Printf("[IN] handle COMMIT_RET %v\n", json_msg)
					prev_hopNid = json_msg.Path[1]
					updateSesOutCap(&json_msg, prev_hopNid, 0)
					trans_ch <- json_msg
				} else if json_msg.Type==Comm.MSG_TYPE_REVERSE_RET {
					// just consume it
					trans_ch <- json_msg
				} else if json_msg.Type==Comm.MSG_TYPE_CONFIRM_RET {
					// just consume it
					trans_ch <- json_msg
				} else {
					// err
					log.Println("[IN] error, supposed to be RET msgs")
				}
			} else {
				// 2) if mid node
				// find the next hop nid first
				need_forward = true
				for i, nid := range(json_msg.Path) {
					if nid == node_conf.NodeID {
						if json_msg.Type==Comm.MSG_TYPE_PROBE || 
						json_msg.Type==Comm.MSG_TYPE_COMMIT ||
						json_msg.Type==Comm.MSG_TYPE_REVERSE || 
						json_msg.Type==Comm.MSG_TYPE_CONFIRM {
							next_hopNid = json_msg.Path[i+1]
						} else {
							next_hopNid = json_msg.Path[i-1]
							prev_hopNid = json_msg.Path[i+1]
							updt_cap_ind = i
						}
						break;
					}
				}

				// just forward to related out_Session since we do calculating at out_Session
				if json_msg.Type==Comm.MSG_TYPE_PROBE {
				} else if json_msg.Type==Comm.MSG_TYPE_PROBE_RET {
				} else if json_msg.Type==Comm.MSG_TYPE_COMMIT {
				} else if json_msg.Type==Comm.MSG_TYPE_COMMIT_RET {
					// update the out_Session capacity
					// do nothing
					if updt_cap_ind < 0 {
						log.Println("[IN] fatal error!!!")
					}
					updateSesOutCap(&json_msg, prev_hopNid, updt_cap_ind)
				}
			}
			

			// if needed, forward msg
			if need_forward == true {
				test_found_flag = false
				for i, _ := range(nd.Sess_out) {
					if next_hopNid == nd.Sess_out[i].NI.NodeID {
						test_found_flag = true
						// fmt.Println(len(nd.Sess_out[i].Msg_ch))
						nd.Sess_out[i].Msg_ch <- json_msg
						break;
					}
				}
				if test_found_flag == false {
					log.Println("[IN] error forward msg!!!", json_msg)
				}
			}
		}

	}
}

func connect_neig() {
	// just sleep some time to wait other nodes 
	time.Sleep(5*time.Second)

	// connect to neighbour
	var err error = nil
	var conn *net.TCPConn 
	var sess Comm.Session
	for _, ngcf := range(neig_conf.Conf) {
		conn, err = net.DialTCP("tcp4", nil, &net.TCPAddr{net.ParseIP(ngcf.Ip), ngcf.Port, ""})
		if err != nil {
			log.Printf("error connect %s:%d\n", ngcf.Ip, ngcf.Port)
		}

		// NOTE: NoDelay is default on
		err = conn.SetKeepAlive(true)
		if err != nil {
			log.Printf("error %s\n", err)
		}
		err = conn.SetKeepAlivePeriod(5*time.Second)
		if err != nil {
			log.Printf("error %s\n", err)
		}

		// add to node
		sess.NI = ngcf
		sess.Conn = *conn
		sess.Cap = ngcf.Cap
		// log.Printf("to nid[%d] cap[%d]\n", sess.NI.NodeID, sess.Cap)
		// make channel
		sess.Msg_ch = make(chan Comm.Msg, 2500)
		sess.N_msg_probe = 0
		sess.N_msg_commit = 0
		sess.N_msg_reverse = 0
		sess.N_msg_confirm = 0
		nd.Sess_out = append(nd.Sess_out, sess)
	}

	// initialize go routine
	for i, _ := range nd.Sess_out {
		go HandleSesOut(&(nd.Sess_out[i]))
	}

	// process trans
	if g_algo == 0 {
		go HandleTrans()
	} else if g_algo == 1 {
		go SP_HandleTrans()
	} else if g_algo == 2 {
		go Spider_HandleTrans()
		// go Spider_HandleTrans_rev()
	} else {
		fmt.Println("algo not defined")
		os.Exit(-1)
	}
}

func read_conf(conf_filename, neig_conf_filename string) {
	// parse node conf file
	conf_data, err := ioutil.ReadFile(conf_filename)
	if err != nil {
		log.Println("err read node_conf file")
		os.Exit(-1)
	}

	err = json.Unmarshal(conf_data, &node_conf)
	if err != nil {
		log.Println("err node_conf json parse")
		os.Exit(-1)
	}
	nd.NI = node_conf

	// parse neighbour conf file
	conf_data, err = ioutil.ReadFile(neig_conf_filename)
	if err != nil{
		log.Println("err read neig_conf file")
		os.Exit(-1)
	}

	err = json.Unmarshal(conf_data, &neig_conf.Conf)
	if err != nil {
		log.Println("err neig_conf json parse")
		os.Exit(-1)
	}
}

func main() {
	// register handler for some signals
	// fmt.Fprintf(os.Stderr, "GoGoGo\n")
	// fmt.Printf("GoGoGo\n")
	go handle_sig()
	var err error = nil
	if 8 > len(os.Args) {
		log.Println("usage: ./server [conf_filename] [neig_conf_filename] [graph_filename] [trans_filename] [path_filename] [#algo] [#ind]")
		os.Exit(-1)
	}
	// get the algo
	g_algo, _ = strconv.Atoi(os.Args[6])
	// get the node id
	g_nodeid, _ = strconv.Atoi(os.Args[7])
	log.Println("g_nodeid", g_nodeid)

	// initialize graph topo and trans
	if init_G(os.Args[3]) == false {
		log.Println("read graph file error")
		os.Exit(-1)
	}
	if load_trans(os.Args[4]) == false {
		log.Println("read trans file error")
		os.Exit(-1)
	}
	if load_paths(os.Args[5]) == false {
		log.Println("read paths file error")
		os.Exit(-1)
	}

	// read configuration
	read_conf(os.Args[1], os.Args[2])

	// initialize the connections
	nd.Ln, err = net.ListenTCP("tcp4", &net.TCPAddr{net.ParseIP(nd.NI.Ip), nd.NI.Port, ""})

	if err != nil {
		log.Println("error node initilization", err)
		os.Exit(-1)
	}

	// connect to neighbour nodes
	go connect_neig()

	// handle incoming connections
	var sess Comm.Session
	for is_active {
		conn, err := nd.Ln.AcceptTCP()

		if err != nil {
			log.Printf("error accept connection %s\n", err)
			continue
		}

		// append to Sess_in
		sess.Conn = *conn
		sess.Msg_ch = make(chan Comm.Msg, 1000)
		nd.Sess_in = append(nd.Sess_in, sess)

		go HandleSesIn(conn)
	}

}
