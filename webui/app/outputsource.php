<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

// List of cities for India
if ($_GET['desttype'] == 'DICOM Sender') {
?>
<table>
<tr><td>Destination Host</td><td><input type='text' name='dest_host' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>Destination Port</td><td><input type='text' name='dest_port' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>AE Title</td><td><input type='text' name='dest_ae_title' oninvalid="alert('You must fill out the form!');" required></td></tr>
</table>
<?php
}
// List of cities for USA
if ($_GET['desttype'] == 'HTTP Sender') {
?>
<table>
<tr><td>Destination URL</td><td><input type='text' name='url' oninvalid="alert('You must fill out the form!');" required></td></tr>
</table>
<?php
}

if ($_GET['desttype'] == 'HTTPS Sender') {
?>
<table>
<tr><td>Destination URL</td><td><input type='text' name='url' oninvalid="alert('You must fill out the form!');" required></td></tr>
</table>
<?php
}
if ($_GET['desttype'] == 'HL7 Sender') {
?>
<table>
<tr><td>Remote Host</td><td><input type='text' name='remote_host' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>Remote Port</td><td><input type='text' name='remote_port' oninvalid="alert('You must fill out the form!');" required></td></tr>
</table>
<?php
}

if ($_GET['desttype'] == 'IOStream Writer') {
?>
<table>
<tr><td>IOStream Host</td><td><input type='text' name='remote_host' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>IOStream Port</td><td><input type='text' name='remote_port' oninvalid="alert('You must fill out the form!');" required></td></tr>
<tr><td>IOStream Queue</td><td><input type='text' name='remote_queue' oninvalid="alert('You must fill out the form!');" required></td></tr>
</table>
<?php
}
?>