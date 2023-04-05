<!DOCTYPE html>
<html>
    <head>
		<link rel="icon" href="img/healthcare-icon.png">
        <title>Healthcare Workflow Integration Engine</title>
    </head>
	<script>
		function dynamic_select_desttype(ajax_page,str) {
			var xmlhttp = new XMLHttpRequest();
			xmlhttp.onreadystatechange = function() {
			  if (this.readyState == 4 && this.status == 200) {
				document.getElementById("txtdestResult").innerHTML = this.responseText;
			  }
			}
			xmlhttp.open("GET", ajax_page+"?desttype="+str, true);
			xmlhttp.send();
		}
		function dynamic_select_sourcetype(ajax_page,str) {
			var xmlhttp = new XMLHttpRequest();
			xmlhttp.onreadystatechange = function() {
			  if (this.readyState == 4 && this.status == 200) {
				document.getElementById("txtsrcResult").innerHTML = this.responseText;
			  }
			}
			xmlhttp.open("GET", ajax_page+"?srctype="+str, true);
			xmlhttp.send();
		}
	</script>
	
	<link rel="stylesheet" href="CSS/site.css">
    <body>
		<img src="img/header.jpg" width="555" height="88">
		<div class="topnav">
		  <a href="index.php">Home</a>
		  <a href="showchannels.php">View existing channels</a>
		  <a class="active" href="createchannel.php">Create channel</a>
		  <a href="about.php">About</a>
		</div>
		<h2> Create channels</h2>
		<form name="cForm" action='savechannel.php' method='POST'> 
			<div class="container">
			  <table>
				<tr><td>Channel Name</td><td><input type='text' name='channelName' oninvalid="alert('You must fill out the form!');" required></td></tr>
				<tr><td>Source Type</td>
				<td>
				<select name="sourceType" id="sourceTypeId"onchange="dynamic_select_sourcetype('inputsource.php', this.value)" style="width=100px" oninvalid="alert('You must fill out the form!');" required>
				  <option></option>
				  <option value="DICOM Listener">DICOM Listener</option>
				  <option value="HTTP Listener">HTTP Listener</option>
				  <option value="HTTPS Listener">HTTPS Listener</option>
				  <option value="HL7 Listener">HL7 Listener</option>
				  <option value="IOStream Reader">IOStream Reader</option>
				</select>
				</td>
				</tr>
			   </table>
			</div>
			<div class="container" id="txtsrcResult"></div>
			<div class="container">
				<table>
					<tr><td>Destination Type</td>
					<td>
					<select name="destType" id="destTypeId" onchange="dynamic_select_desttype('outputsource.php', this.value)" style="width=100px" oninvalid="alert('You must fill out the form!');" required>
					  <option></option>
					  <option value="DICOM Sender">DICOM Sender</option>
					  <option value="HTTP Sender">HTTP Sender</option>
					  <option value="HTTPS Sender">HTTPS Sender</option>
					  <option value="HL7 Sender">HL7 Sender</option>
					  <option value="IOStream Writer">IOStream Writer</option>
					</select>
					</td>
					</tr>
				</table>
			</div>
			<div class="container" id="txtdestResult"></div>
			</br>
			</br>
			<input type='submit' name='submit' value='Submit'>
			</form>
    </body>
</html>
