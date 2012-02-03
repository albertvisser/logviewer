<?php
$sts = array();
$sts['100'] = 'Continue';
$sts['101'] = 'Switching Protocols';
$sts['200'] = 'OK';
$sts['201'] = 'Created';
$sts['202'] = 'Accepted';
$sts['203'] = 'Non-Authoritative Information';
$sts['204'] = 'No Content';
$sts['205'] = 'Reset Content';
$sts['206'] = 'Partial Content';
$sts['300'] = 'Multiple Choices';
$sts['301'] = 'Moved Permanently';
$sts['302'] = 'Found';
$sts['303'] = 'See Other';
$sts['304'] = 'Not Modified';
$sts['305'] = 'Use Proxy';
$sts['306'] = '(Unused)';
$sts['307'] = 'Temporary Redirect';
$sts['400'] = 'Bad Request';
$sts['401'] = 'Unauthorized';
$sts['402'] = 'Payment Required';
$sts['403'] = 'Forbidden';
$sts['404'] = 'Not Found';
$sts['405'] = 'Method Not Allowed';
$sts['406'] = 'Not Acceptable';
$sts['407'] = 'Proxy Authentication Required';
$sts['408'] = 'Request Timeout';
$sts['409'] = 'Conflict';
$sts['410'] = 'Gone';
$sts['411'] = 'Length Required';
$sts['412'] = 'Precondition Failed';
$sts['413'] = 'Request Entity Too Large';
$sts['414'] = 'Request-URI Too Long';
$sts['415'] = 'Unsupported Media Type';
$sts['416'] = 'Requested Range Not Satisfiable';
$sts['417'] = 'Expectation Failed';
$sts['500'] = 'Internal Server Error';
$sts['501'] = 'Not Implemented';
$sts['502'] = 'Bad Gateway';
$sts['503'] = 'Service Unavailable';
$sts['504'] = 'Gateway Timeout';
$sts['505'] = 'HTTP Version Not Supported';
function showerror($x) {
    $r = array("referer"=>'',"client"=>'',"date"=>'',"data"=>'');
    $h = explode(', referer: ',$x);
    if (count($h) > 1) {
        $r["referer"] = $h[1];
        }
    $h = explode('] ',$h[0],4);
    //~ print_r($h); echo "\n";
    if (count($h) > 1) {
        $r['date'] = substr($h[0],1).' : '.substr($h[1],1);
        if (count($h) > 2) {
            $r['client'] = substr($h[2],7);
            if (count($h) > 3) {
                $r['data'] = $h[3];
                if (substr($h[3],strlen($h[3])-2) == '\\r')
                    $r['data'] = substr($h[3],0,strlen($h[3])-2);
            }
            else
                $r['data'] = $h[2];
        }
    }
    return $r;
}
function showaccess($x) {
    global $sts;
    $r = array('client'=>'','date'=>'','data'=>'');
    $h = explode(' -',$x,2);
    $r['client'] = $h[0];
    //~ print_r($h); echo "\n";
    if (count($h) > 1) {
        $h = explode(' [',$h[1]);
        //~ print_r($h); echo "\n";
        if (count($h) > 1) {
            $h = explode('] "',$h[1]);
            $r['date'] = $h[0];
            //~ print_r($h); echo "\n";
            if (count($h) > 1) {
                $h = explode('" ',$h[1]);
                $d = $h[0];
                //~ print_r($h); echo "\n";
                if (count($h) > 1) {
                    $h = explode(' ',$h[1]);
                    $r['data'] = $h[0].' '.$sts[$h[0]].': '.$d;
                    //~ print_r($h); echo "\n";
                }
                else
                    $r['data'] = $d;
            }
        }
    }
    return $r;
}
?>
