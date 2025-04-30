osascript -e 'tell app "Terminal" to do script "sh /opt/ibc/twsstartmacos.sh -inline"'
osascript -e 'tell app "Terminal" to do script "python \"$DIT_ROOT/dit-email-to-order.py\""' 
osascript -e 'tell app "Terminal" to do script "python \"$DIT_ROOT/dit-order-to-tws.py\""' 
