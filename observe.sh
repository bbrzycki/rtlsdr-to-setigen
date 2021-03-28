rtl_sdr -s 2048000 -f 90300000 -n infinite test.dat &
TASK_PID=$!
sleep 60
kill $TASK_PID