<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">

<head profile="http://gmpg.org/xfn/11">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>佩吉布林打卡門 &raquo; pagebrin dot com</title>
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-8345312-1']);
  _gaq.push(['_trackPageview']);
  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>
</head>

<body>

<h1> Index of /mobi magazines </h1>
<p>
本页面提供根据南方周末，南都周刊，南方人物周刊网站提供的RSS输出以周单位集结而成的电子杂志，每周五准时出刊。
</br>所提供电子杂志的格式为标准的.mobi，可在任何支持mobi格式的终端和软件上阅读，对<a href="http://kindle.amazon.com" target="_blank">Amazon Kindle</a>进行特别优化。
</p>
<table><tr><th><img src="blank.gif" alt="[ICO]"></th><th><a href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last modified</a></th><th><a href="?C=S;O=A">Size</a></th><th><a href="?C=D;O=A">Description</a></th></tr><tr><th colspan="5"><hr></th></tr> 

<?php

function format_bytes($bytes) {
   if ($bytes < 1024) return $bytes.' B';
   elseif ($bytes < 1048576) return round($bytes / 1024, 2).' KB';
   elseif ($bytes < 1073741824) return round($bytes / 1048576, 2).' MB';
}

$dir = './';
if ($handle = opendir($dir)){
  $line = array();
  $line_sub = array();
  while (false !== ($file = readdir($handle))){
    $file_path_1 = $dir.$file;
    if ($result = ereg("\.mobi$",$file)){
      unset($line_sub);
      $ctime = filemtime($file_path_1);
      while (array_key_exists($ctime,$line))
        $ctime += 1;
      $csize = format_bytes(filesize($file_path_1));
      $line_sub[] = $file;
      $line_sub[] = $csize;
      $line[$ctime] = $line_sub;
    }
  }
  closedir($handle);

  krsort($line);
  foreach($line as $key => $value){
    $filename = $value[0];
    $file_path_2 = $dir.$filename;
    $display_time = date ("m/d/Y", $key);
    $filesize = $value[1];
    print "\n".'<tr><td valign="top"><img src="icon.png" alt="[   ]"></td>';
    print '<td><a href="'.$file_path_2.'">'.$filename.'</a></td>';
    print '<td align="right">'.$display_time.'</td>';
    print '<td align="right">'.$filesize.'</td>';
    print '<td>&nbsp;</td></tr> ';
  }
}
?>

<tr><th colspan="5"><hr></th></tr> 
</table> 
<address> Powered by pagebrin.com & 
  <a href="http://twitter.com/#!/Bill_JaJa" target="_blank">@Bill_JaJa</a>
</address> 

</body>
</html>