<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

// List of cities for India
if ($_GET['ch'] == 'India') {
?>
<select name="cityList">
<option value="Mumbai">Mumbai</option>
<option value="Delhi">Delhi</option>
<option value="Bangalore">Bangalore</option>
<option value="Patna">Patna</option>
</select>
<?php
}
// List of cities for USA
if ($_GET['ch'] == 'USA') {
?>
<select name="cityList">
<option value="Albama">Albama</option>
<option value="Alaska">Alaska</option>
<option value="Arizona">Arizona</option>
<option value="Florida">Florida</option>
</select>
<?php
}
?>