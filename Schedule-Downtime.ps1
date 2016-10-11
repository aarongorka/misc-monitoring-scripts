Param(
  [string]$Hostname = $env:COMPUTERNAME.ToLower(),
  [string]$Username,
  [string]$Password,
  [string]$Comment = "Powershell-automated downtime from " + $env:COMPUTERNAME.ToLower(),
  [string]$NagiosServer,
  [int]$Minutes = 120
)

[Reflection.Assembly]::LoadWithPartialName("System.Web") > $null
$url = "https://$NagiosServer/nagios/cgi-bin/cmd.cgi";
$ajax = new-object -com msxml2.xmlhttp;
$ajax.open("POST",$url,$false, $Username,
    $password);
$ajax.setRequestHeader("Content-Type",
    "application/x-www-form-urlencoded");
$startTime = "{0:yyyy-MM-dd} {0:HH:mm:ss}" -f (Get-Date);
$endTime = "{0:yyyy-MM-dd} {0:HH:mm:ss}" -f ((Get-Date) + (New-TimeSpan -Minutes $minutes));
$postStrMain = "cmd_typ=55&cmd_mod=2&"+
    "com_author=" + $Username + "&"+ 
    "com_data=" + $Comment + "&"+
    "trigger=0&"+ 
    "start_time="+
    [System.Web.HttpUtility]::UrlEncode($startTime)+"&"+
    "end_time="+
    [System.Web.HttpUtility]::UrlEncode($endTime) +"&"+
    "fixed=1&hours=2&minutes=0&childoptions=0&btnSubmit=Commit";
$str = "host="+[System.Web.HttpUtility]::UrlEncode($hostName)+
    "&"+$postStrMain;
$ajax.setRequestHeader("Content-Length", $str.length);
$ajax.send($str);
