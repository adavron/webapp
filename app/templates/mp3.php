<?php
$mp3 = $_GET['mp3'];
$file = $mp3;
if(ini_get('zlib.output_compression')) {
 ini_set('zlib.output_compression', 'Off');
}
if ( file_exists($file) ) {
 header("Pragma: public");
 header('Expires: '.gmdate('D, d M Y H:i:s').' GMT');
 header("Cache-Control: must-revalidate, post-check=0, pre-check=0");
 header("Cache-Control: private",false);
 header("Content-Type: application/mp3");
 header('Content-Disposition: attachment; filename="'.$mp3.'"');
 header("Content-Transfer-Encoding: binary");
 header("Content-Length: ".@filesize($file));
 set_time_limit(0);
 @readfile($file) OR die("<html><body OnLoad=\"javascript: alert('Unable to read file!');history.back();\" bgcolor=\"#F0F0F0\"></body></html>");
 exit;
} else {
 die("<html><body OnLoad=\"javascript: alert('File not found!');history.back();\" bgcolor=\"#F0F0F0\"></body></html>");
}
?>
