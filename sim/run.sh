for num in 1000 2000 3000 4000 5000 6000
do
        # Raw results for Fig. 6, 7 and 8
        nohup python main.py ripple $num general > ripple-$num.out 2>&1 &
        nohup python main.py lightning $num general > lightning-$num.out 2>&1 &
done

# Raw results for Fig. 10
nohup python main.py ripple 2000 threshold > ripple-threshold.out 2>&1 &
nohup python main.py lightning 2000 threshold > lightning-threshold.out 2>&1 &

# Raw results for Fig. 11
nohup python main.py ripple 2000 cache & > ripple-cache.out 2>&1 &
nohup python main.py lightning 2000 cache & > lightning-cache.out 2>&1 &
