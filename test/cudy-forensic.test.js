'use strict';

const assert = require('assert');

const {
  mapQueryPath,
  emulatorBaseFromUrl,
  sameEmulatorScope,
  luciStaticRelative,
  bodyPairsToQuery,
  outputPathForUrl,
  disambiguateOutputPath
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


run('keeps extensionless and .html URL responses distinct', function () {
  const base = emulatorBaseFromUrl(
    'https://support.cudy.com/emulator/LT500/cgi-bin/luci/admin/system/backup'
  );

  const a = outputPathForUrl(
    'https://support.cudy.com/emulator/LT500/cgi-bin/luci/admin/system/backup',
    'text/html; charset=utf-8',
    base
  );
  const b = outputPathForUrl(
    'https://support.cudy.com/emulator/LT500/cgi-bin/luci/admin/system/backup.html',
    'text/html; charset=utf-8',
    base
  );

  assert.strictEqual(a, b);

  const b2 = disambiguateOutputPath(
    b,
    'https://support.cudy.com/emulator/LT500/cgi-bin/luci/admin/system/backup.html',
    0
  );

  assert.notStrictEqual(a, b2);
  assert.ok(/__u_[0-9a-f]{12}\.html$/.test(b2));
});


run('preserves real image and font extensions when cache-busting query strings are present', function () {
  const base = emulatorBaseFromUrl(
    'https://support.cudy.com/emulator/C200P/'
  );

  const png = outputPathForUrl(
    'https://support.cudy.com/emulator/C200P/luci-static/light/img/logo-blue.png?v=git-26.169.24995-88fd143',
    'image/png',
    base
  );
  const svg = outputPathForUrl(
    'https://support.cudy.com/emulator/C200P/luci-static/resources/logo.svg?v=git-26.169.24995-88fd143',
    'image/svg+xml',
    base
  );
  const woff2 = outputPathForUrl(
    'https://support.cudy.com/emulator/C200P/luci-static/light/css/iconfont.woff2?v=git-26.169.24995-88fd143',
    'font/woff2',
    base
  );

  assert.ok(/logo-blue__q_[0-9a-f]{12}\.png$/.test(png), png);
  assert.ok(/logo__q_[0-9a-f]{12}\.svg$/.test(svg), svg);
  assert.ok(/iconfont__q_[0-9a-f]{12}\.woff2$/.test(woff2), woff2);
  assert.strictEqual(/\.bin$/.test(png), false);
  assert.strictEqual(/\.bin$/.test(svg), false);
  assert.strictEqual(/\.bin$/.test(woff2), false);
});

run('uses MIME-derived extensions for extensionless assets', function () {
  const base = emulatorBaseFromUrl(
    'https://support.cudy.com/emulator/C200P/'
  );

  assert.ok(/\.png$/.test(outputPathForUrl(
    'https://support.cudy.com/emulator/C200P/assets/logo?id=1',
    'image/png',
    base
  )));
  assert.ok(/\.svg$/.test(outputPathForUrl(
    'https://support.cudy.com/emulator/C200P/assets/diagram?id=1',
    'image/svg+xml',
    base
  )));
});
