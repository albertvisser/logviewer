<html>
<head>
    <title>Albert's Simple Log Viewer</title>
    <script type="text/javascript">
        function settop(x) {
            e = document.getElementById('top_line');
            if (x == 'first' || x == 'last') {
                e.value = x;
            }
            else {
                var c = 'ok';
                if (e.value == 'last' && x == "next") {
                    c = 'nok';
                }
                else if (e.value == 'first' && x == "prev") {
                    c = 'nok';
                }
                else {
                }
                if (c == 'ok' && x == 'next') {
                }
                if (c == 'ok' && x == 'prev') {
                }
            }
        }
    </script>
    <?php
    include('readlog.php');
    // lees de input variabelen
    // print_r($_POST);
    $logdir = '/var/log/nginx';
    if (array_key_exists('logfile',$_POST))
        $_logfile = $_POST["logfile"];
    else
        $_logfile = '';
    if (array_key_exists('entries',$_POST))
        $_entries= $_POST["entries"];
    else
        $_entries= '10';
    if (array_key_exists('top_line',$_POST))
        $_first = $_POST["top_line"];
    else
        $_first = 'last';
    if (array_key_exists('order',$_POST))
        $_order = $_POST["order"];
    else
        $_order = 'desc';
    $numentries = array('5','10','15','20','25','30');
    // als eerste keer: lees log directory en toon lijst met filenamen
    //~ $files = scandir($logdir);
    //~ $files = array_filter(glob($logdir . '/*.log'),'basename');
    $files = array();
    $times = array();
    foreach (glob($logdir . '/*.log') as $name) {
//        if (substr($name, -1, 3) == 'log') {
            $files[] = basename($name);
            $times[] = filemtime($name);
//        };
    };
    array_multisort($times, SORT_DESC, $files);
    //~ print_r($_logfile); echo "\n";
    $iserrorlog = strpos($_logfile,'error');
    if (substr($_logfile, 0, 5) == 'error')
        $iserrorlog = true;
    //~ print_r($iserrorlog); echo "\n";
    ?>
</head>
<body style="color: white; background-color: black">
    <!-- <div style="colour: black; background-color: orange"><h2>Albert's Simple Log Viewer</h2></div> -->
    <form action="viewlogs.php" method='post'>
    <div>
        <span style="float: left; width:20%">Kies een log bestand:</span>
        <span>
            <select name="logfile" id="logfile" onchange="submit()"><?php
            foreach ($files as $entry) {
            if (! is_dir($entry)) {
                ?><option
                <?php if ($entry == $_logfile) echo ' selected="selected"'; ?>
                >
                <?php echo $entry; ?></option><?php
            }} ?>
            </select>
        </span>
        <span>
            <input type="submit" value="nu verversen/laatste" onclick="settop('last');return true"/>
            <!--
            <input type="button" value="vorige" onclick="settop('prev');submit();return true"/>
            <input type="button" value="volgende" onclick="settop('next');submit();return true"/>
            <input type="button" value="eerste" onclick="settop('first');submit();return true"/>
            -->
        </span>
    </div>
    <div>
        <span style="float: left; width:20%">Aantal entries per pagina:</span>
        <span>
            <select name="entries" id="entries" onchange="submit()"><?php
            foreach ($numentries as $num) {
                ?>
                <option
                <?php if ($num == $_entries) echo ' selected="selected"'; ?>
                >
                <?php echo $num; ?></option><?php
            }?>
            </select>
        </span>
        <span style="padding-left: 212px">Volgorde:</span>
        <span>
            <input type="radio" name="order" value="desc" onclick="submit()" <?php
            if ($_order == "desc") echo 'checked="checked"';?>/>&nbsp;nieuwste eerst&nbsp;
            <input type="radio" name="order" value="asc" onclick="submit()" <?php
            if ($_order == "asc") echo 'checked="checked"';?>/>&nbsp;nieuwste laatst&nbsp;
        </span>
    </div>
    <div>
        <table>
            <tr>
                <th>When</th><th>What</th><th>Where</th>
            </tr><?php
        $lines = 1;
        if ($_logfile != '') {
            $f = file($logdir.'/'.$_logfile);
            if ($_order == "desc") {
                //~ for ($i=count($f)-1;$i>=count($f)-intval($_entries)&&$i>=0;$i--) {
                $i = count($f)-1;
                while ($i >= count($f)-intval($_entries)&&$i>=0) {
                    ?><tr><?php
                    //~ print_r($iserrorlog); echo "\n";
                    if ($iserrorlog) {
                        $r = showerror(rtrim($f[$i]));
                        //~ print_r($r); echo "\n";
                        echo '<td><textarea style="font-size: 8pt" rows="4" cols="25">'.$r["date"].'</textarea></td><td><textarea style="font-size: 8pt" rows="4" cols="70">'.$r["data"].'</textarea></td><td><textarea style="font-size: 8pt" rows="4" cols="35">'.$r["referer"].' from'.$r["client"].'</textarea></td>';
                    }
                    else{
                        $r = showaccess(rtrim($f[$i]));
                        //~ print_r($r); echo "\n";
                        echo '<td><textarea font-size: 8pt" rows="4" cols="25">'.$r["date"].'</textarea></td><td><textarea font-size: 8pt" rows="4" cols="60">'.$r["data"].'</textarea></td><td><textarea font-size: 8pt" rows="4" cols="25">'.$r["client"].'</textarea></td>';
                    }
                    ?></tr><?php
                    $i--;
                    $lines++;
                }
            }
            else {
                //~ for ($i=count($f)-intval($_entries);$i<=count($f)-1;$i++) {
                $i = count($f)-intval($_entries);
                if ($i < 1) $i = 0;
                while ($i < count($f)) {
                    ?><tr><?php
                    if ($iserrorlog) {
                        $r = showerror(rtrim($f[$i]));
                        echo '<td><textarea style="font-size: 8pt" rows="4" cols="25">'.$r["date"].'</textarea></td><td><textarea style="font-size: 8pt" rows="4" cols="70">'.$r["data"].'</textarea></td><td><textarea style="font-size: 8pt" rows="4" cols="35">'.$r["referer"].'</textarea></td>';
                    }
                    else{
                        $r = showaccess(rtrim($f[$i]));
                        echo '<td><textarea rows="2" cols="25">'.$r["date"].'</textarea></td><td><textarea rows="2" cols="60">'.$r["data"].'</textarea></td><td><textarea rows="2" cols="25">'.$r["client"].'</textarea></td>';
                    }
                    ?></tr><?php
                    $i++;
                    $lines++;
                }
            }
        }
        for ($i=$lines;$i<=intval($_entries);$i++) {
            if ($iserrorlog) {
            ?><tr><td><textarea style="font-size: 8pt" rows="4" cols="25"></textarea></td><td><textarea style="font-size: 8pt" rows="4" cols="70"></textarea></td><td><textarea style="font-size: 8pt" rows="4" cols="35"></textarea></td></tr><?php
            }
            else {
            ?><tr><td><textarea rows="2" cols="25"></textarea></td><td><textarea rows="2" cols="60"></textarea></td><td><textarea rows="2" cols="25"></textarea></td></tr><?php
            }
        }
        ?></table>
    </div>
    <div>
        <input type="hidden" id="first_time" value="False"/>
        <input type="hidden" id="top_line" value="last"/>
    </div>
    </form>
</body>
</html>
