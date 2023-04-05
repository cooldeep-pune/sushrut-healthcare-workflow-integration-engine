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
	  <a href="index.php">Home</a>
	  <a class="active" href="showchannels.php">View existing channels</a>
	  <a href="createchannel.php">Create channel</a>
	  <a href="about.php">About</a>
	</div>
        <p>
		<h2>Channels</h2>
		<form method="post" action="">
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
			    $str_check = '<input type="checkbox" id="checkItem" name="check[]" value="'.$row[0].'">'.$row[0];
				echo "<tr><td>$str_check</td><td>$row[1]</td><td>$row[2]</td><td>$row[3]</td></tr>";
			}

			pg_close($con);

			?>
		  </table>
		</div>
			</br>
		    <button type="submit" class="btn btn-primary" style="width:200px" name="view">View Channel</button>
			</br>
        </form>
		<div>
				<?php
				$host = getenv("POSTGRES_HOST"); 
				$user = getenv("POSTGRES_USER"); 
				$pass = getenv("POSTGRES_PASSWORD");  
				$db = getenv("POSTGRES_DB"); 
				$con = pg_connect("host=$host dbname=$db user=$user password=$pass")
				or die ("Could not connect to server\n"); 
				if(isset($_POST['view']))
				{
				   $checkbox = $_POST['check'];         
						for($i=0;$i<count($checkbox);$i++){
							$check_id = $checkbox[$i];
							$query = "select content from healthcare_channels where channel_id ='$check_id'"; 
							$rs = pg_query($con, $query) or die("Cannot execute query: $query\n");
							while ($row = pg_fetch_row($rs)) {
								$json_string = json_encode(json_decode($row[0]), JSON_PRETTY_PRINT);
								echo '<pre>' . $json_string . '</pre>';
							}
							break;
					   }
				}
				?>
		</div>
        </p>
    </body>
</html>
