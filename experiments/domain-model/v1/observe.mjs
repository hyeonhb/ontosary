import ts from 'typescript';
import path from 'node:path';
import { createHash } from 'node:crypto';
export const sha = data => createHash('sha256').update(data).digest('hex');
export function observeRoles(program, spec, root, diagnostics = []) {
  const checker = program.getTypeChecker();
  const relative = file => path.relative(root, file);
  const source = file => program.getSourceFile(path.join(root, file));
  const findClass = target => source(target.file)?.statements.find(n => ts.isClassDeclaration(n) && n.name?.text === target.name);
  const findMember = target => findClass(target)?.members.find(n => n.name && (ts.isIdentifier(n.name) || ts.isStringLiteral(n.name)) && n.name.text === target.member);
  const targets = new Map(spec.attributes.map(a => [a.id, a.targets.map(findMember)]));
  const evidence = node => {
    const sf = node.getSourceFile(), offset = node.getStart(sf), end = node.getEnd();
    return { file: relative(sf.fileName), symbol: node.name?.getText(sf) ?? ts.SyntaxKind[node.kind], offset, end,
      line: sf.getLineAndCharacterOfPosition(offset).line + 1, anchor: sf.text.slice(offset, end), sha256: sha(sf.text) };
  };
  const objects = [], facts = [];
  for (const selected of spec.classes) {
    const cls = findClass(selected);
    if (!cls) throw new Error(`Missing selected class: ${selected.name}`);
    for (const method of cls.members.filter(ts.isMethodDeclaration).filter(n => n.name)) {
      const e = evidence(method), id = `${spec.revision}:${e.file}:${e.offset}`;
      const object = { id, class: selected.name, name: method.name.getText(), evidence: { ...e, anchor: e.anchor.split('\n')[0] }, cells: {} };
      objects.push(object);
      const calls = [];
      const visit = n => { if (ts.isClassDeclaration(n) || ts.isClassExpression(n)) return; if (ts.isCallExpression(n)) calls.push(n); ts.forEachChild(n, visit); };
      if (method.body) visit(method.body);
      for (const attribute of spec.attributes) {
        const found = [], uncertain = [];
        if (!method.body) uncertain.push('method body unavailable');
        if (diagnostics.length) uncertain.push('compilation diagnostics prevent a complete binary observation');
        const declarations = targets.get(attribute.id);
        if (declarations.some(d => !d)) uncertain.push('target declaration unavailable');
        for (const call of calls) {
          let callee = call.expression;
          while (ts.isParenthesizedExpression(callee)) callee = callee.expression;
          if (!ts.isPropertyAccessExpression(callee) && !ts.isElementAccessExpression(callee)) continue;
          if (attribute.arguments === 'zero' && call.arguments.length !== 0) continue;
          if (attribute.arguments === 'positive' && call.arguments.length === 0) continue;
          const member = ts.isPropertyAccessExpression(callee) ? callee.name : callee.argumentExpression;
          if (!member || (!ts.isIdentifier(member) && !ts.isStringLiteral(member) && !ts.isNumericLiteral(member)) || (ts.isElementAccessExpression(callee) && !ts.isStringLiteral(member) && !ts.isNumericLiteral(member))) {
            uncertain.push('nonliteral computed member call'); continue;
          }
          if (!attribute.targets.some(t => t.member === member.text)) continue;
          let symbol = checker.getSymbolAtLocation(member);
          if (symbol?.flags & ts.SymbolFlags.Alias) symbol = checker.getAliasedSymbol(symbol);
          if (!symbol?.declarations?.length || checker.getTypeAtLocation(callee.expression).flags & (ts.TypeFlags.Any | ts.TypeFlags.Unknown)) {
            uncertain.push(`unresolved member call: ${member.text}`); continue;
          }
          const matches = symbol.declarations.filter(d => declarations.includes(d));
          if (matches.length && matches.length !== symbol.declarations.length) uncertain.push('ambiguous target declarations');
          else if (matches.length) found.push(evidence(call));
        }
        // Any uncertainty prevents a binary cell even if another occurrence is known.
        const value = uncertain.length ? 'unknown' : found.length ? 'yes' : 'no';
        const fact = { id: `cell:${id}:${attribute.id}`, kind: 'observed-in-source', author: 'automated-observer', method: 'typescript-ast-symbol-identity',
          scope: 'Direct member call expressions in lexical method region, including nested callbacks/functions, excluding nested classes; no reachability/transitive-call claim',
          support: value === 'unknown' ? 'unresolved' : 'supported-static-role', claim: attribute.label, object: id, attribute: attribute.id, value,
          reasons: [...new Set(uncertain)], evidence: found.length ? found : [object.evidence] };
        facts.push(fact); object.cells[attribute.id] = { value, factRef: fact.id };
      }
    }
  }
  return { objects, facts, targets: spec.attributes.map(a => ({ id: a.id, declarations: targets.get(a.id).map(d => d ? evidence(d) : null) })) };
}
export function binaryContext(observation, attributes) {
  if (observation.facts.some(f => f.value === 'unknown')) return { status: 'unknown-cells', context: null };
  return { status: 'binary', context: { objects: observation.objects.map(o => o.id).sort(), attributes: attributes.map(a => a.id).sort(),
    incidence: Object.fromEntries(observation.objects.map(o => [o.id, attributes.filter(a => o.cells[a.id].value === 'yes').map(a => a.id).sort()])) } };
}
