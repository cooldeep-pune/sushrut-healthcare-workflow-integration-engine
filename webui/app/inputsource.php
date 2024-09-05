<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

if ($_GET['srctype'] == 'DICOM Listener') {
?>
<table>
<tr><td>Port</td><td><input type='text' name='src_port' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>AE Title</td><td><input type='text' name='src_ae_title' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>Source transformer</td><td><input type='text' name='src_transform'></td></tr>
</table>
<?php
}
if ($_GET['srctype'] == 'HTTP Listener') {
?>
<table>
<tr><td>Port</td><td><input type='text' name='src_port' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>Source transformer</td><td><input type='text' name='src_transform'></td></tr>
</table>
<?php
}
if ($_GET['srctype'] == 'HTTPS Listener') {
?>
<table>
<tr><td>Port</td><td><input type='text' name='src_port' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>Source transformer</td><td><input type='text' name='src_transform'></td></tr>
</table>
<?php
}
if ($_GET['srctype'] == 'HL7 Listener') {
?>
<table>
<tr><td>Port</td><td><input type='text' name='src_port' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>Source transformer</td><td><input type='text' name='src_transform'></td></tr>
</table>
<?php
}

if ($_GET['srctype'] == 'IOStream Reader') {
?>
<table>
<tr><td>IOStream Host</td><td><input type='text' name='src_host' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>IOStream Port</td><td><input type='text' name='src_port' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>IOStream Queue</td><td><input type='text' name='src_queue' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>Source transformer</td><td><input type='text' name='src_transform'></td></tr>
</table>
<?php
}
?>