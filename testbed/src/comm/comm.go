package Comm

import (
	"net"
	"sync"
)

const MSG_TYPE_PROBE = 1
const MSG_TYPE_PROBE_RET = 2
const MSG_TYPE_COMMIT = 3
const MSG_TYPE_COMMIT_RET = 4
const MSG_TYPE_REVERSE = 5
const MSG_TYPE_REVERSE_RET = 6
const MSG_TYPE_CONFIRM = 7
const MSG_TYPE_CONFIRM_RET = 8
const NUM_MAX_CONN = 10

// paths processed offline
type Path struct {
	Nid		[]int
}

//
type Potential_path struct {
	Nid			[]int
	ActCommit	float32
	Capacity	float32
}

type ByCapacity []Potential_path

//
type NodeInfo struct {
	NodeID	int		`json:"nid"`
	Ip		string	`json:"ip"`
	Port	int		`json:"port"`
	Cap		float32		`json:"cap"`
}

// conf-related
type NodeConf struct {
	Conf	NodeInfo
}

type NeigConf struct {
	Conf	[]NodeInfo
}

// trans-related
type Trans struct {
	Src			int
	Dst			int
	Volume		float32	
}

// msg-related
type Msg struct {
	Type		int				`json:"type"`
	TransID		int				`json:"tid"`
	ReqID		int				`json:"rid"`
	Src			int				`json:"src"`
	Dst			int				`json:"dst"`
	Reverse		float32			`json:"rev"`
	Path		[]int			`json:"path"`
	Cap			[]float32		`json:"cap"`
	P1c			[]float32		`json:"p1c`		// log down phase-1 commit 
	Commit		float32			`json:"commit"`
	ActCommit	float32			`json:"actcom"`
}

// node-related 
type Session struct {
	NI		NodeInfo		// I copy an capacity outside it
	Msg_ch	chan Msg
	Conn	net.TCPConn
	Cap		float32
	CapLock	sync.Mutex		// lock for var Cap
	N_msg_probe	int
	N_msg_commit	int
	N_msg_reverse	int
	N_msg_confirm	int
}

type Node struct {
	NI		NodeInfo
	Ln		*net.TCPListener
	Sess_out	[]Session
	Sess_in		[]Session
}
