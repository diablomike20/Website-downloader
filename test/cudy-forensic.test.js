'use strict';

const assert = require('assert');

const {
  mapQueryPath,
  emulatorBaseFromUrl,
  sameEmulatorScope,
  luciStaticRelative,
  bodyPairsToQuery
} = require('../cudy/forensic');

function run(name, fn) {
  try {
    fn();
    console.log('PASS ' + name);
  } catch (err) {
    console.error('FAIL ' + name);
    throw err;
  }
}

run('maps Cudy query path exactly', function () {
  assert.strictEqual(
    mapQueryPath('cgi-bin/luci/admin/system/autoupgrade?updatecheck=&nomodal='),
    'cgi-bin/luci/admin/system/autoupgrade/updatecheck/nomodal'
  );
});

run('maps LuCI URL into static emulator snapshot', function () {
  const page = 'https://support.cudy.com/emulator/C200P/cgi-bin/luci/admin/system/autoupgrade.html';
  const base = emulatorBaseFromUrl(page);

  assert.strictEqual(
    luciStaticRelative(
      '/cgi-bin/luci/admin/system/autoupgrade?updatecheck=&nomodal=',
      page,
      base,
      ''
    ),
    'cgi-bin/luci/admin/system/autoupgrade/updatecheck/nomodal.html'
  );
});

run('maps simple $.post body into snapshot path', function () {
  const page = 'https://support.cudy.com/emulator/C200P/cgi-bin/luci/admin/system/autoupgrade.html';
  const base = emulatorBaseFromUrl(page);
  const body = bodyPairsToQuery("token: 'abc123'");

  assert.strictEqual(body, 'token=abc123');
  assert.strictEqual(
    luciStaticRelative(
      '/cgi-bin/luci/admin/system/autoupgrade/updatecheck',
      page,
      base,
      body
    ),
    'cgi-bin/luci/admin/system/autoupgrade/updatecheck/token/abc123.html'
  );
});

run('scope lock stays inside one emulator model', function () {
  const base = emulatorBaseFromUrl(
    'https://support.cudy.com/emulator/C200P/cgi-bin/luci/admin/setup.html'
  );

  assert.strictEqual(
    sameEmulatorScope(
      'https://support.cudy.com/emulator/C200P/luci-static/light/js/cbi.js',
      base
    ),
    true
  );

  assert.strictEqual(
    sameEmulatorScope(
      'https://support.cudy.com/emulator/TR3000/',
      base
    ),
    false
  );
});

console.log('fu_6 Cudy forensic mapper tests complete.');
