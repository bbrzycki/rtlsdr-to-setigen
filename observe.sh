#!/bin/bash

# Echo usage if something isn't right.
usage() { 
    echo "Usage: $0 [-f FREQUENCY] [-s SAMPLE_RATE] [-t TIME] [-d DESTINATION]" 1>&2; exit 1; 
}

SAMPLE_RATE=2048000
while getopts ":f:s:t:d:" o; do
    case "${o}" in
        f)
            FREQUENCY=${OPTARG}
            ;;
        s)
            SAMPLE_RATE=${OPTARG}
            ;;
        t)  
            TIME=${OPTARG}
            ;;
        d)  
            DESTINATION=${OPTARG}
            ;;
        :)  
            echo "ERROR: Option -$OPTARG requires an argument"
            usage
            ;;
        \?)
            echo "ERROR: Invalid option -$OPTARG"
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Check required switches exist
if [ -z "${f}" ] || [ -z "${t}" ] || [ -z "${d}" ]; then
    usage
fi

rtl_sdr -f $FREQUENCY -s $SAMPLE_RATE -n infinite $DESTINATION &
TASK_PID=$!
# Give small time buffer for observation length
ADJ_TIME=$(python -c "print($TIME * 1.01)")
sleep $ADJ_TIME
kill $TASK_PID


