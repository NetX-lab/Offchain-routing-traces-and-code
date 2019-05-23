package Comm


import (
	// "log"
	// "fmt"
)

const G_SIZE = 1000
const PATH_NOT_PROBED = 0
const PATH_INITED = -1

func is_visited(path *[]int, node int) bool {
	var ret = false
	for i, _ := range *path {
		if (*path)[i] == node {
			ret = true
			break
		}
	}
	return ret
}

func Find_path_cap(G *[G_SIZE+1][G_SIZE+1]float32, path []int) float32 {
	var capacity float32 = -1
	var path_valid bool = true
	for i:=0; i<=len(path)-2; i++ {
		path_cap := (*G)[path[i]][path[i+1]]
		if (path_cap < 0) {
			path_valid = false
		}
		if path_valid == true {
			if capacity<0 || (path_cap<capacity&&path_cap>0) {
				capacity = path_cap
			}
		}
	}
	return capacity
}

func Bfs_shortest_path(G *[G_SIZE+1][G_SIZE+1]float32, src, dst, g_size int) ([]int, bool) {
	var found bool = false
	var path []int = make([]int, 0)
	var visited [G_SIZE+1]bool
	var prev_node [G_SIZE+1]int
	var que []int
	var node int 

	for i:=0; i<G_SIZE+1; i++ {
		visited[i] = false
		prev_node[i] = 0
	}

	que = append(que, src)
	visited[src] = true

	for 0 < len(que) {
		node, que = que[0], que[1:]

		for i:=1; i<=g_size; i++ {
			if i!=node && visited[i]==false && ((*G)[node][i]>0 || (*G)[node][i]==PATH_INITED) {
				// fmt.Println(i)
				visited[i] = true
				prev_node[i] = node
				que = append(que, i)
				if i==dst {
					found = true
					break
				}
			}
		}
	}

	// generate path
	if found==true {
		nid := dst
		for nid != src {
			path = append([]int{nid}, path...)
			nid = prev_node[nid]
		}
		path = append([]int{src}, path...)
	}
	return path, found
}

func Bfs(G *[G_SIZE+1][G_SIZE+1]float32, src, dst, npath, g_size int) ([][]int) {
	var paths [][]int = make([][]int, 0)
	var n_found_paths int = 0


	var que [][]int
	var path []int = make([]int, 0)
	var last_n int
	var newpath []int
	path = append(path, src)
	que = append(que, path)

	for 0 < len(que) {
		path, que = que[0], que[1:]

		last_n = path[len(path)-1]
		if dst == last_n {
			paths = append(paths, path)
			n_found_paths = n_found_paths+1
			if n_found_paths >= npath {
				break
			}
		}

		for i:=1; i<=g_size; i++ {
			if (*G)[last_n][i]==PATH_INITED || (*G)[last_n][i]>0 {
				if is_visited(&path, i) == false {
					// var newpath []int = append(path, i)
					newpath = append(path, i)
					// log.Println(newpath)
					que = append(que, newpath)
					// log.Printf("%d\n", len(que))
					newpath = newpath[:0]
				}
			}
		}

	}
	return paths
}
