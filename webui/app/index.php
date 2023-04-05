<!DOCTYPE html>
<html>
    <head>
		<link rel="icon" href="img/healthcare-icon.png">
        <title>Healthcare Workflow Integration Engine</title>
    </head>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="CSS/site.css">
    <body>
	<img src="img/header.jpg" width="555" height="88">
	<div class="topnav">
	  <a class="active" href="index.php">Home</a>
	  <a href="showchannels.php">View existing channels</a>
	  <a href="createchannel.php">Create channel</a>
	  <a href="about.php">About</a>
	</div>
        <p>
		<h2> Deployed Channels</h2>
		<div style="overflow-x: auto;">
		  <table>
			<tr>
			  <th>Channel ID</th>
			  <th>Channel Name</th>
			  <th>Source Type</th>
			  <th>Destination Type</th>
			</tr>
			<?php 

			$host = getenv("POSTGRES_HOST"); 
			$user = getenv("POSTGRES_USER"); 
			$pass = getenv("POSTGRES_PASSWORD");  
			$db = getenv("POSTGRES_DB"); 

			$con = pg_connect("host=$host dbname=$db user=$user password=$pass")
				or die ("Could not connect to server\n"); 

			$query = "select channel_id as id,content -> 'channel' -> 'name'as name ,content -> 'channel' -> 'sourceConnector'-> 'transportName' as sourcetype, content -> 'channel' ->'destinationConnectors'->'connector' -> 'transportName' as desttype from healthcare_channels where channel_id in (select deployed_channel_id from channels_deployed);"; 

			$rs = pg_query($con, $query) or die("Cannot execute query: $query\n");

			while ($row = pg_fetch_row($rs)) {
				echo "<tr><td>$row[0]</td><td>$row[1]</td><td>$row[2]</td><td>$row[3]</td></tr>";
			}

			pg_close($con);

			?>
		  </table>
		</div>
        </p>
		<p>
		<h2>Channels</h2>
		<div style="overflow-x: auto;">
		  <table>
			<tr>
			  <th>Channel ID</th>
			  <th>Channel Name</th>
			  <th>Source Type</th>
			  <th>Destination Type</th>
			</tr>
			<?php 

			$host = getenv("POSTGRES_HOST"); 
			$user = getenv("POSTGRES_USER"); 
			$pass = getenv("POSTGRES_PASSWORD");  
			$db = getenv("POSTGRES_DB"); 

			$con = pg_connect("host=$host dbname=$db user=$user password=$pass")
				or die ("Could not connect to server\n"); 

			$query = "select channel_id as id,content -> 'channel' -> 'name'as name ,content -> 'channel' -> 'sourceConnector'-> 'transportName' as sourcetype, content -> 'channel' ->'destinationConnectors'->'connector' -> 'transportName' as desttype from healthcare_channels;"; 

			$rs = pg_query($con, $query) or die("Cannot execute query: $query\n");

			while ($row = pg_fetch_row($rs)) {
				echo "<tr><td>$row[0]</td><td>$row[1]</td><td>$row[2]</td><td>$row[3]</td></tr>";
			}

			pg_close($con);

			?>
		  </table>
		</div>
        </p>
    </body>
</html>
