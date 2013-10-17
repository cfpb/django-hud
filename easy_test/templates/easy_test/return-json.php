<?php

sleep(3);

$data = array(
  'zip' => array(
    'zipcode' => '22030',
    'lat' => '38.8462',
    'lng' => '-77.3279',
  ),
  'counseling_agencies' => array(
    'id1' => array(
      'name' => 'Pizzeria Orso',
      'addr' => '400 S Maple Ave  Falls Church, VA 22046',
      'lat' => '38.880576',
      'lng' => '-77.176873',
    ),
    'id2' => array(
      'name' => '2941',
      'addr' => '400 S Maple Ave  Falls Church, VA 22046',
      'lat' => '38.5330',
      'lng' => '-77.0123',
    ),
    'id3' => array(
      'name' => 'Chipotle',
      'addr' => '400 S Maple Ave  Falls Church, VA 22046',
      'lat' => '38.5076',
      'lng' => '-77.1824',
    ),
  ),
  'error' => null,
);
exit();

echo json_encode( $data );
