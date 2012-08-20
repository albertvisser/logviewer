<html>
<head>
    <title>Albert's Simple Log Viewer</title>
</head>
<body style="color: white; background-color: black">
    <!-- <div style="colour: black; background-color: orange"><h2>Albert's Simple Log Viewer</h2></div> -->
    <form action="/" method='get'>
    <div>
        <span style="float: left; width:20%">Kies een log bestand:</span>
        <span>
            <select name="logfile" id="logfile" onchange="submit()">
            % for dir in loglist:
                <option
                %if dir == logfile:
                    selected="selected"
                %end
                >{{ dir }}</option>
            %end
            </select>
        </span>
        <span>
            <input type="submit" value="verversen" />
            <a href="/top" title="eerste pagina"><input type="button" value="begin" /></a>
            <a href="/prev" title="vorige pagina"><input type="button" value="vorige" /></a>
            <a href="/next" title="volgende pagina"><input type="button" value="volgende" /></a>
            <a href="/bottom" title="laatste pagina"><input type="button" value="eind" /></a>
        </span>
    </div>
    <div>
        <span style="float: left; width:20%">Aantal entries per pagina:</span>
        <span>
            <select name="entries" id="entries" onchange="submit()">
            %for num in numentries:
                <option
                %if num == entries:
                    selected="selected"
                %end
                >{{ num }}</option>
            %end
            </select>
        </span>
        <span style="padding-left: 212px">Volgorde:</span>
        <span>
            <input type="radio" name="order" value="desc" onclick="submit()"
            %if order == "desc":
                checked="checked"
            %end
            />&nbsp;nieuwste eerst&nbsp;
            <input type="radio" name="order" value="asc" onclick="submit()"
            %if order == "asc":
                checked="checked"
            %end
            />&nbsp;nieuwste laatst&nbsp;
        </span>
    </div>
    <div style="text-align: center">{{mld}}&nbsp;</div>
    <div>
        <table>
            <tr>
                <th>When</th><th>What</th><th>Where</th>
            </tr>
            %for data in logdata:
            <tr>
                %if errorlog:
                <td>
                <textarea style="font-size: 8pt" rows="2" cols="25">{{data['date']}}</textarea>
                </td>
                <td>
                <textarea style="font-size: 8pt" rows="2" cols="70">{{data['data']}}</textarea>
                </td>
                <td>
                <textarea style="font-size: 8pt" rows="2" cols="35">{{data['client']}}</textarea>
                </td>
                %else:
                <td>
                <textarea style ="font-size: 8pt" rows="2" cols="25">{{data['date']}}</textarea>
                </td>
                <td>
                <textarea style="font-size: 8pt" rows="2" cols="60">{{data['data']}}</textarea>
                </td>
                <td>
                <textarea style="font-size: 8pt" rows="2" cols="25">{{data['client']}}</textarea>
                </td>
                % end
            </tr>
            %end
        </table>
    </div>
    </form>
</body>
</html>
