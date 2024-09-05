<?php

function save_to_database($channel_id,$channel_name,$content) {
	$host = getenv("POSTGRES_HOST"); 
	$user = getenv("POSTGRES_USER"); 
	$pass = getenv("POSTGRES_PASSWORD");  
	$db = getenv("POSTGRES_DB"); 
	//$json = addslashes($content);
	
	$con = pg_connect("host=$host dbname=$db user=$user password=$pass")
		or die ("Could not connect to server\n"); 

	$query = "insert into healthcare_channels(channel_id,channel_name,content) values('$channel_id','$channel_name','{$content}')"; 
	
	
	$rs = pg_query($con, $query) or die("Cannot execute query: $query\n");

	pg_close($con);

}
function gen_uuid() {
    return sprintf( '%04x%04x-%04x-%04x-%04x-%04x%04x%04x',
        // 32 bits for "time_low"
        mt_rand( 0, 0xffff ), mt_rand( 0, 0xffff ),

        // 16 bits for "time_mid"
        mt_rand( 0, 0xffff ),

        // 16 bits for "time_hi_and_version",
        // four most significant bits holds version number 4
        mt_rand( 0, 0x0fff ) | 0x4000,

        // 16 bits, 8 bits for "clk_seq_hi_res",
        // 8 bits for "clk_seq_low",
        // two most significant bits holds zero and one for variant DCE1.1
        mt_rand( 0, 0x3fff ) | 0x8000,

        // 48 bits for "node"
        mt_rand( 0, 0xffff ), mt_rand( 0, 0xffff ), mt_rand( 0, 0xffff )
    );
}

if(isset($_POST['submit']))
{
	$src_class = "";
	$dest_class = "";
	
	if ($_POST['sourceType'] == 'DICOM Listener') {
		$src_class = "healthcare-workflow/dicom-receiver";		
	} elseif ($_POST['sourceType'] == 'HTTP Listener') {
		$src_class = "healthcare-workflow/http-receiver";	
	} elseif ($_POST['sourceType'] == 'HL7 Listener') {
		$src_class = "healthcare-workflow/hl7-receiver";
	} elseif ($_POST['sourceType'] == 'IOStream Reader') {
		$src_class = "healthcare-workflow/iostream-reader";
	} elseif ($_POST['sourceType'] == 'HTTPS Listener') {
		$src_class = "healthcare-workflow/https-receiver";	
	}
	
	if ($_POST['destType'] == 'DICOM Sender') {
		$dest_class = "healthcare-workflow/dicom-sender";		
	} elseif ($_POST['destType'] == 'HTTP Sender') {
		$dest_class = "healthcare-workflow/http-sender";	
	} elseif ($_POST['destType'] == 'HL7 Sender') {
		$dest_class = "healthcare-workflow/hl7-sender";
	} elseif ($_POST['destType'] == 'IOStream Writer') {
		$dest_class = "healthcare-workflow/iostream-writer";
	} elseif ($_POST['destType'] == 'HTTPS Sender') {
		$dest_class = "healthcare-workflow/https-sender";	
	} 
	
	
	$uuid = gen_uuid();
	$postArray = array();
	
	if(empty($_POST['src_transform'])) {
		$postArray = array(
			"channel" => array(
				"id" => $uuid,
				"name" => $_POST['channelName'],
				"sourceConnector" => array(
					"transportName" => $_POST['sourceType'],
					"properties" => array(
						"@class" => $src_class,
						"applicationEntity" => $_POST['src_ae_title'],
						"queue_name" => $_POST['src_queue'],
						"listenerConnectorProperties" => array(
							"port" => $_POST['src_port'],
							"host" => $_POST['src_host']
						)
					)
				),
				"destinationConnectors" => array(
					"connector" => array(
						"transportName" => $_POST['destType'],
						"properties" => array(
							"@class" => $dest_class,
							"applicationEntity" => $_POST['dest_ae_title'],
							"port" => $_POST['dest_port'],
							"host" => $_POST['dest_host'],
							"remoteAddress" =>$_POST['remote_host'],
							"remotePort" =>$_POST['remote_port'],
							"remote_queue" => $_POST['remote_queue'],
							"url" => $_POST['url']
						)
					)
				)
			)
		); 

	} else {
		$postArray = array(
			"channel" => array(
				"id" => $uuid,
				"name" => $_POST['channelName'],
				"sourceConnector" => array(
					"transportName" => $_POST['sourceType'],
					"properties" => array(
						"@class" => $src_class,
						"applicationEntity" => $_POST['src_ae_title'],
						"queue_name" => $_POST['src_queue'],
						"listenerConnectorProperties" => array(
							"port" => $_POST['src_port'],
							"host" => $_POST['src_host']
						)
					),
					"transformer" => array(
						"@class" => $_POST['src_transform']
					)
				),
				"destinationConnectors" => array(
					"connector" => array(
						"transportName" => $_POST['destType'],
						"properties" => array(
							"@class" => $dest_class,
							"applicationEntity" => $_POST['dest_ae_title'],
							"port" => $_POST['dest_port'],
							"host" => $_POST['dest_host'],
							"remoteAddress" =>$_POST['remote_host'],
							"remotePort" =>$_POST['remote_port'],
							"remote_queue" => $_POST['remote_queue'],
							"url" => $_POST['url']
						)
					)
				)
			)
		); 
	}

	$json = json_encode( $postArray );
	save_to_database($uuid,$_POST['channelName'],$json);
	
    header("Location:showchannels.php");
	exit();
}
?>