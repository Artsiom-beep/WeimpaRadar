<?php
// run.php

set_time_limit(0);
ini_set('max_execution_time', '0');

function slug($s) {
  $s = trim(strtolower($s));
  $s = preg_replace('/^https?:\/\//', '', $s);
  $s = rtrim($s, '/');
  $s = preg_replace('/[^a-z0-9\.\-_]+/', '-', $s);
  return $s ?: 'site';
}

function ensure_dir($path) {
  if (!is_dir($path)) mkdir($path, 0777, true);
}

function save_upload($fileKey, $dstPath) {
  if (!isset($_FILES[$fileKey])) return false;
  if ($_FILES[$fileKey]['error'] !== UPLOAD_ERR_OK) return false;
  return move_uploaded_file($_FILES[$fileKey]['tmp_name'], $dstPath);
}

function save_uploads_array($fileKey, $dstDir, $prefix) {
  if (!isset($_FILES[$fileKey])) return;
  $f = $_FILES[$fileKey];
  if (!is_array($f['name'])) return;

  $count = count($f['name']);
  for ($i = 0; $i < $count; $i++) {
    if (($f['error'][$i] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) continue;

    $name = $f['name'][$i] ?? '';
    $ext = strtolower(pathinfo($name, PATHINFO_EXTENSION));
    if ($ext === 'jpeg') $ext = 'jpg';
    if (!in_array($ext, ['png', 'jpg'], true)) $ext = 'png';

    $dst = $dstDir . DIRECTORY_SEPARATOR . sprintf('%s_%02d.%s', $prefix, $i + 1, $ext);
    move_uploaded_file($f['tmp_name'][$i], $dst);
  }
}

$client_domain = trim($_POST['client_domain'] ?? '');
$market = trim($_POST['market'] ?? 'Global');
$language = trim($_POST['language'] ?? 'en');
$mode = trim($_POST['mode'] ?? 'sales');
$competitor_1 = trim($_POST['competitor_1'] ?? '');
$slide_limit = intval($_POST['slide_limit'] ?? 0);

$semrush_auto = isset($_POST['semrush_auto']) && $_POST['semrush_auto'] === '1';
$semrush_db = trim($_POST['semrush_db'] ?? 'pl');

if ($client_domain === '') {
  http_response_code(400);
  echo "client_domain is required";
  exit;
}

$run_id = date('Y-m-d') . '__' . slug($client_domain) . '__' . $mode . '__' . $language;

$base = __DIR__;
$runs_dir = $base . DIRECTORY_SEPARATOR . 'runs';
$run_dir  = $runs_dir . DIRECTORY_SEPARATOR . $run_id;
$uploads_dir = $run_dir . DIRECTORY_SEPARATOR . 'uploads';

ensure_dir($uploads_dir);

// manual semrush images
save_uploads_array('semrush_files', $uploads_dir, 'semrush');

// optional semrush pdf
save_upload('semrush_pdf', $uploads_dir . DIRECTORY_SEPARATOR . 'semrush.pdf');

// optional blocked
save_upload('blocked_screen', $uploads_dir . DIRECTORY_SEPARATOR . 'blocked_screen.png');

$competitors = [];
if ($competitor_1 !== '') $competitors[] = $competitor_1;

$payload = [
  'cmd' => 'run',
  'client_domain' => $client_domain,
  'market' => $market,
  'language' => $language,
  'mode' => $mode,
  'competitors' => $competitors,
  'run_id' => $run_id,
  'semrush_auto' => $semrush_auto,
  'semrush_db' => $semrush_db,
];

if ($slide_limit > 0) $payload['slide_limit'] = $slide_limit;

$json = json_encode($payload, JSON_UNESCAPED_UNICODE);

// ВАЖНО для Windows: -X utf8
$cmd = 'python -X utf8 py/cli.py';

$descriptors = [
  0 => ['pipe', 'r'],
  1 => ['pipe', 'w'],
  2 => ['pipe', 'w']
];

$proc = proc_open($cmd, $descriptors, $pipes, $base);
if (!is_resource($proc)) {
  http_response_code(500);
  echo "Failed to start python";
  exit;
}

fwrite($pipes[0], $json);
fclose($pipes[0]);

$out = stream_get_contents($pipes[1]);
$err = stream_get_contents($pipes[2]);
fclose($pipes[1]);
fclose($pipes[2]);

$code = proc_close($proc);

$res = json_decode($out, true);
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Radar result</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 980px; margin: 24px auto; padding: 0 12px; }
    pre { white-space: pre-wrap; background:#f6f6f6; padding: 12px; border:1px solid #ddd; }
    img { max-width: 980px; border:1px solid #ddd; }
  </style>
</head>
<body>
  <h1>Result</h1>

  <pre><?php
    echo htmlspecialchars("exit_code=$code\n\nstdout:\n$out\n\nstderr:\n$err");
  ?></pre>

  <?php if (is_array($res) && ($res['ok'] ?? false)): ?>
    <?php $runDirRel = 'runs/' . $run_id; ?>
    <h2>Artifacts</h2>
    <ul>
      <li><a href="<?php echo $runDirRel . '/sales_note.txt'; ?>">sales_note.txt</a></li>
      <li><a href="<?php echo $runDirRel . '/report.md'; ?>">report.md</a></li>
      <li><a href="<?php echo $runDirRel . '/data.json'; ?>">data.json</a></li>
      <li><a href="<?php echo $runDirRel . '/data.csv'; ?>">data.csv</a></li>
    </ul>

    <h2>Screenshots</h2>
    <?php
      $ssDirRel = $runDirRel . '/screenshots';
      $ssDirAbs = __DIR__ . DIRECTORY_SEPARATOR . $ssDirRel;
      if (is_dir($ssDirAbs)) {
        $files = scandir($ssDirAbs);
        foreach ($files as $f) {
          if ($f === '.' || $f === '..') continue;
          if (!preg_match('/\.(png|jpg|jpeg|webp)$/i', $f)) continue;
          $src = $ssDirRel . '/' . $f;
          echo '<div style="margin:10px 0;">';
          echo '<div>' . htmlspecialchars($f) . '</div>';
          echo '<img src="' . htmlspecialchars($src) . '" />';
          echo '</div>';
        }
      }
    ?>
  <?php endif; ?>
</body>
</html>
