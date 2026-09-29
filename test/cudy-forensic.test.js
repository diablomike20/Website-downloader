'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');

const {
  mapQueryPath,
  emulatorBaseFromUrl,
  sameEmulatorScope,
  luciStaticRelative,
  bodyPairsToQuery
} = require('../cudy/forensic');

test('maps Cudy query path exactly', () => {
  assert.equal(
    mapQueryPath('cgi-bin/luci/admin/system/autoupgrade?updatecheck=&nomodal='),
    'cgi-bin/luci/admin/system/autoupgrade/updatecheck/nomodal'
  );
});

test('maps LuCI URL into static emulator snapshot', () => {
  const page = 'https://support.cudy.com/emulator/C200P/cgi-bin/luci/admin/system/autoupgrade.html';
  const base = emulatorBaseFromUrl(page);

  assert.equal(
    luciStaticRelative(
      '/cgi-bin/luci/admin/system/autoupgrade?updatecheck=&nomodal=',
      page,
      base,
      ''
    ),
    'cgi-bin/luci/admin/system/autoupgrade/updatecheck/nomodal.html'
  );
});

test('maps simple $.post body into snapshot path', () => {
  const page = 'https://support.cudy.com/emulator/C200P/cgi-bin/luci/admin/system/autoupgrade.html';
  const base = emulatorBaseFromUrl(page);
  const body = bodyPairsToQuery("token: 'abc123'");

  assert.equal(body, 'token=abc123');
  assert.equal(
    luciStaticRelative(
      '/cgi-bin/luci/admin/system/autoupgrade/updatecheck',
      page,
      base,
      body
    ),
    'cgi-bin/luci/admin/system/autoupgrade/updatecheck/token/abc123.html'
  );
});

test('scope lock stays inside one emulator model', () => {
  const base = emulatorBaseFromUrl(
    'https://support.cudy.com/emulator/C200P/cgi-bin/luci/admin/setup.html'
  );

  assert.equal(
    sameEmulatorScope(
      'https://support.cudy.com/emulator/C200P/luci-static/light/js/cbi.js',
      base
    ),
    true
  );

  assert.equal(
    sameEmulatorScope(
      'https://support.cudy.com/emulator/TR3000/',
      base
    ),
    false
  );
});
