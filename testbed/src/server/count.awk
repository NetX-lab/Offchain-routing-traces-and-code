BEGIN{t_ovh=0;n_succ=0;n_fail=0;succ_vol=0;n_node=0;n_probe=0;n_commit=0;n_reverse=0;n_confirm=0;t_s_ovh=0;t_l_ovh=0}
n_node += 1;
t_s_ovh += $2;
t_l_ovh += $3;
t_ovh += $4;
n_succ += $5;
n_fail += $6;
succ_vol += $7;
n_probe += $8;
n_commit += $9;
n_reverse += $10;
n_confirm += $11;
END{rate=n_succ/(n_succ+n_fail);
	t_ovh = t_ovh/n_node;
	t_s_ovh = t_s_ovh/n_node;
	t_l_ovh = t_l_ovh/n_node;
	print "s_ovh:",t_s_ovh,"l_ovh:",t_l_ovh,"succ:",n_succ,"fail:",n_fail,"succ_ratio:",rate,"succ_vol:",succ_vol,"t_ovh:",t_ovh,"n_probe:",n_probe,"n_commit:",n_commit,"n_reverse:",n_reverse,"n_confirm:",n_confirm}


