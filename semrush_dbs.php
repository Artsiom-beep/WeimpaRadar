<?php
header('Content-Type: application/json; charset=utf-8');

$dbs = [
  "us","uk","ca","au",
  "de","fr","es","it","nl","pl","se","no","dk","fi",
  "ch","at","be","ie","pt","cz","sk","hu","ro","gr",
  "tr","il","ae","sa","eg","za",
  "in","pk","bd","lk",
  "sg","my","id","th","vn","ph","hk","tw","jp","kr",
  "br","mx","ar","cl","co","pe"
];

echo json_encode([
  "ok" => true,
  "dbs" => $dbs
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
