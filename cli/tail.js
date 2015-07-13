#!/usr/bin/env node
'use strict';

var ArgumentParser = require('argparse').ArgumentParser;
var io = require('socket.io-client')

var parser = new ArgumentParser({
  version: '0.0.1',
  addHelp: true,
  description: 'Totem Logs CLI'
});
parser.addArgument(
    [ '-o', '--owner' ],
    {
      help: 'SCM Owner'
    }
);
parser.addArgument(
    [ '-r', '--repo' ],
    {
      help: 'SCM Repository'
    }
);
parser.addArgument(
    [ '-b', '--ref' ],
    {
      help: 'SCM Ref(branch/tag)'
    }
);
parser.addArgument(
    [ '-p', '--program-name' ],
    {
      help: 'Optional Program name (overrides SCM info)'
    }
);
parser.addArgument(
    [ '-a', '--after-date' ],
    {
      help: 'Fetch logs after given date/time in ISO format (e.g.: 2015-07-11T06:30:58-07:00)'
    }
);
parser.addArgument(
    [ '-u', '--url' ],
    {
      help: 'Log Service URL'
    }
);
var args = parser.parseArgs();

var baseUrl = args.url || 'http://localhost:9500'
console.log('Connecting to log service at ' +baseUrl+'/logs');

var socket = io.connect(baseUrl+'/logs');

socket.on('connect', function () {
  socket.emit('fetch', {
    'after-date': args.after_date,
    interval: 5,
    'meta-info': {
      'git': {
        'owner': args.owner,
        'repo': args.repo,
        'ref': args.ref
      }
    },
    'program-name': args.program_name
  });
  console.log('Waiting for logs....');
});


socket.on('logs', function (logs) {
  logs.forEach(function (log) {
    console.log(log.message);
  });
});

socket.on('status', function (status) {
  if (status['type'] === 'FAILED') {
    console.log(status.description);
    process.exit(1);
  }
});
