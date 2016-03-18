<?php
/* PUT data comes in on the stdin stream */
$putdata = fopen("php://input", "r");
$loc = $_SERVER['PATH_INFO'];
$loc_split = explode("/",$loc);
$leng = count($loc_split);
print_r($loc_split);
unset($loc_split[$leng-1]);
print_r($loc_split);

$pth = implode('/',$loc_split);
mkdir($pth, 0777, true);

/* Open a file for writing */
$fp = fopen($_SERVER['PATH_INFO'], "w");  ##FUCK IT WE HAVE DIRECTORY TRAVERSAL
print_r(error_get_last());
/* Read the data 1 KB at a time
   and write to the file */
while ($data = fread($putdata, 1024))
  fwrite($fp, $data);

/* Close the streams */
fclose($fp);
fclose($putdata);
echo $_SERVER['PATH_INFO']
?>

