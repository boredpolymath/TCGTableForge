import test from 'node:test';
import assert from 'node:assert/strict';
import '../data.js';

const { LIMITS, makeExport, validateImport } = globalThis.TableForgeData;

function project(overrides = {}) {
  return {
    projectId: 'p1', name: 'Example', approach: 'world-first', description: '', designGoals: '',
    createdAt: '2026-01-01T00:00:00.000Z', updatedAt: '2026-01-01T00:00:00.000Z',
    cards: [
      { cardId: 'c1', projectId: 'p1', type: 'World', title: 'Place', notes: '', createdAt: '2026-01-01T00:00:00.000Z', updatedAt: '2026-01-01T00:00:00.000Z' },
      { cardId: 'c2', projectId: 'p1', type: 'Mechanic', title: 'Rule', notes: '', createdAt: '2026-01-01T00:00:00.000Z', updatedAt: '2026-01-01T00:00:00.000Z' }
    ],
    relationships: [{ relationshipId: 'r1', projectId: 'p1', fromCardId: 'c1', toCardId: 'c2', label: 'Supports', createdAt: '2026-01-01T00:00:00.000Z' }],
    ...overrides
  };
}

test('version 1 export validates and preserves project content', () => {
  const source = makeExport(project());
  assert.deepEqual(validateImport(source), source.project);
});

test('versionless legacy imports normalize old card type names without mutating input', () => {
  const old = project({ cards: [
    { cardId: 'c1', type: 'World Idea', title: 'Place', notes: '' },
    { cardId: 'c2', type: 'Player Experience', title: 'Feeling', notes: '' }
  ], relationships: [{ relationshipId: 'r1', fromCardId: 'c1', toCardId: 'c2', label: 'Creates Tension With' }] });
  const normalized = validateImport(old);
  assert.deepEqual(normalized.cards.map(card => card.type), ['World', 'Experience']);
  assert.equal(old.cards[0].type, 'World Idea');
});

test('unsupported explicit schema versions are rejected', () => {
  assert.throws(() => validateImport({ schemaVersion: 2, project: project() }), /not supported/);
});

test('duplicate IDs and missing relationship endpoints are rejected', () => {
  const duplicate = project({ cards: [project().cards[0], project().cards[0]] });
  assert.throws(() => validateImport(makeExport(duplicate)), /Card IDs must be unique/);
  const missing = project({ relationships: [{ relationshipId: 'r1', fromCardId: 'c1', toCardId: 'absent', label: 'Supports' }] });
  assert.throws(() => validateImport(makeExport(missing)), /missing card/);
  const duplicateRelationships = project({ relationships: [
    { relationshipId: 'r1', fromCardId: 'c1', toCardId: 'c2', label: 'Supports' },
    { relationshipId: 'r1', fromCardId: 'c2', toCardId: 'c1', label: 'Expresses' }
  ] });
  assert.throws(() => validateImport(makeExport(duplicateRelationships)), /Relationship IDs must be unique/);
});

test('file size, card count, and custom label limits are enforced', () => {
  assert.throws(() => validateImport(project(), LIMITS.importBytes + 1), /10 MB or smaller/);
  const tooMany = project({ cards: Array.from({ length: LIMITS.cards + 1 }, (_, i) => ({ cardId: `c${i}`, type: 'World', title: 'x', notes: '' })) });
  assert.throws(() => validateImport(tooMany), /larger than the supported import limit/);
  assert.throws(() => validateImport(project({ customRelationshipLabels: ['x'.repeat(LIMITS.relationshipLabel + 1)] })), /longer than/);
});

test('documented boundary sizes are accepted', () => {
  const bounded = project({
    cards: Array.from({ length: LIMITS.cards }, (_, i) => ({ cardId: `c${i}`, type: 'World', title: 'T'.repeat(LIMITS.title), notes: '' })),
    relationships: Array.from({ length: LIMITS.relationships }, (_, i) => ({ relationshipId: `r${i}`, fromCardId: 'c0', toCardId: 'c1', label: 'Supports' }))
  });
  bounded.padding = '';
  const baseLength = Buffer.byteLength(JSON.stringify(bounded));
  bounded.padding = 'x'.repeat(LIMITS.importBytes - baseLength);
  const exactBytes = Buffer.byteLength(JSON.stringify(bounded));
  assert.equal(exactBytes, LIMITS.importBytes);
  const accepted = validateImport(bounded, exactBytes);
  assert.equal(accepted.cards.length, LIMITS.cards);
  assert.equal(accepted.relationships.length, LIMITS.relationships);

  const maximumFields = project({ cards: [
    { cardId: 'c1', type: 'World', title: 'T'.repeat(LIMITS.title), notes: 'n'.repeat(LIMITS.notes) }
  ], relationships: [] });
  assert.equal(validateImport(maximumFields, Buffer.byteLength(JSON.stringify(maximumFields))).cards[0].notes.length, LIMITS.notes);
});
