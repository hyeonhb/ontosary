import {build} from 'vite';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const source = path.resolve(process.argv[2]), out = path.resolve(process.argv[3]);
const seams = path.join(here, 'seams.jsx');
const providers = [
    'virtual:vendure-ui-config', '@lingui/react/macro', 'lucide-react', '@tanstack/react-query', 'sonner',
    '../orders.graphql.js', '@/vdb/constants.js', '@/vdb/graphql/api.js', '@/vdb/lib/utils.js',
    '@/vdb/hooks/use-dynamic-translations.js', '@/vdb/hooks/use-local-format.js',
    '@/vdb/components/shared/vendure-image.js',
    ...['alert','button','checkbox','dialog','label','select'].map(n => '@/vdb/components/ui/'+n+'.js'),
];
const routes = path.join(source, 'app/routes/_authenticated/_orders');
await build({ configFile: false, root: here, logLevel: 'error', publicDir: false,
    resolve: {alias: [
        {find: 'control-dialog', replacement: path.join(routes, 'components/refund-order-dialog.tsx')},
        {find: '@/vdb/components/ui/input.js', replacement: path.join(source,'lib/components/ui/input.tsx')},
        ...providers.map(find => ({find, replacement:seams})),
        ...['react','react-dom'].map(find => ({find, replacement:path.dirname(require.resolve(find+'/package.json'))})),
    ]},
    define: {'process.env.NODE_ENV': JSON.stringify('production')},
    oxc: {jsx: {runtime:'automatic'}},
    build: {outDir:out, minify:false, lib: {entry:path.join(here,'observe.jsx'), name:'QuantityProbe',
        formats:['iife'], fileName:()=> 'probe.js'}},
});
fs.writeFileSync(path.join(out, 'index.html'),
    '<meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'self\'"><div id="mount"></div><pre id="result"></pre><script src="./probe.js"></script>');
