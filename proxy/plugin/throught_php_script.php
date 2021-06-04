<?php

$pass = "1234";

//ini_set('error_reporting', E_ALL);
//ini_set('display_errors', 1);

if (!isset($_SERVER['HTTP_X_TEST_PASS'])) exit();
if ($pass !== $_SERVER['HTTP_X_TEST_PASS']) exit();

$host = $_SERVER['HTTP_X_TEST_HOST'];
$request = $_SERVER['HTTP_X_TEST_URL'];
$host_scheme = (!isset($_SERVER['HTTP_X_TEST_SHEME'])) ? "https" : "http";
$url = $host_scheme . '://' . $host . $request;

$headers = "host: " . $host . "\r\n" . "connection: close" . "\r\n";
foreach ($_SERVER as $name => $value) {
    if (in_array($name, ['HTTP_VIA', 'HTTP_HOST', 'HTTP_CONNECTION']))
        continue;
    $parts = explode('_', $name);
    if (count($parts) < 2 || $parts[0] != 'HTTP' || $parts[1] == 'X')
        continue;
    array_shift($parts);
    $name = strtolower(implode('-', $parts));
    $headers .= $name . ': ' . $value . "\r\n";
}

$context = stream_context_create([
    'http' => [
        'ignore_errors'   => true,
        'follow_location' => false,
        'method'          => $_SERVER['REQUEST_METHOD'],
        'header'          => $headers,
        'timeout'         => 30,
        'content'         => http_build_query($_POST)
    ]]);

$result = file_get_contents($url, false, $context);

if (!isset($http_response_header)) {
    http_response_code(404);
    die("Proxy error. Can not access.");
}

foreach ($http_response_header as $header_line) {
    header($header_line, false);
    // may be filter? str_replace($proxy_host, $host, $value)
    // $a = preg_split('~[ :;,\/\\\\]+~', trim(strtolower($header_line)));
    // if ('content-type' == $a[0]) $c_type = $a;
}

//if (isset($c_type) && in_array($c_type[1], ['text', 'application']) &&
//    in_array($c_type[2], ['html', 'css', 'xml', 'xhtml+xml', 'javascript'])) { }

echo $result;
?>

