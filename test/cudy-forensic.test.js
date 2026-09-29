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


run('discovers HTML-escaped modal actions such as Backup and SSH', function () {
  const page = 'https://support.cudy.com/emulator/C200P/cgi-bin/luci/admin/panel.html';
  const base = emulatorBaseFromUrl(page);
  const html = [
    '<button onclick="cbi_show_modal(&quot;#cbi-modal&quot;, &quot;/cgi-bin/luci/admin/system/backup&quot;, &quot;&quot;, &quot;&quot;);return false">Backup</button>',
    '<button onclick="cbi_show_modal(&quot;#cbi-modal&quot;, &quot;/cgi-bin/luci/admin/system/ssh&quot;, &quot;&quot;, &quot;&quot;);return false">SSH</button>'
  ].join('');

  const refs = require('../cudy/forensic').extractReferences(
    html,
    'text/html; charset=utf-8',
    page,
    base
  );

  assert.strictEqual(
    refs.routes.has('https://support.cudy.com/emulator/C200P/cgi-bin/luci/admin/system/backup'),
    true
  );
  assert.strictEqual(
    refs.routes.has('https://support.cudy.com/emulator/C200P/cgi-bin/luci/admin/system/ssh'),
    true
  );
});


run('discovers model-prefixed legacy LuCI route strings', function () {
  const page = 'https://support.cudy.com/emulator/LT500/cgi-bin/luci/admin/setup';
  const base = emulatorBaseFromUrl(page);
  const html = '<script>var u="/emulator/LT500/cgi-bin/luci/admin/system/backup";</script>';

  const refs = require('../cudy/forensic').extractReferences(
    html,
    'text/html; charset=utf-8',
    page,
    base
  );

  assert.strictEqual(
    refs.routes.has('https://support.cudy.com/emulator/LT500/cgi-bin/luci/admin/system/backup'),
    true
  );
});
