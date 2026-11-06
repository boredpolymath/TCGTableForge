((root, factory) => {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.TableForgeData = api;
})(globalThis, () => {
  const TYPES = ['World', 'Experience', 'Theme', 'Mechanic', 'Question'];
  const TYPE_ALIASES = {
    'World Idea': 'World',
    'Player Experience': 'Experience',
    'Open Question': 'Question'
  };
  const BUILTIN_LABELS = ['Supports', 'Expresses', 'Creates Tension With', 'Depends On'];
  const LIMITS = Object.freeze({
    importBytes: 10 * 1024 * 1024,
    cards: 5000,
    relationships: 10000,
    title: 120,
    notes: 3000,
    name: 100,
    description: 500,
    designGoals: 300,
    relationshipLabel: 50,
    customRelationshipLabels: 100
  });

  const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const text = (value, max, label, required = false) => {
    if (typeof value !== 'string' || (required && !value.trim())) {
      throw new Error(`${label} must be ${required ? 'non-empty ' : ''}text.`);
    }
    if (value.length > max) throw new Error(`${label} is longer than ${max} characters.`);
    return value;
  };
  const stamp = value => typeof value === 'string' && value.length <= 100 ? value : new Date().toISOString();

  function validateImport(source, fileSize = 0) {
    if (fileSize > LIMITS.importBytes) throw new Error('Project files must be 10 MB or smaller.');
    if (!object(source)) throw new Error('The file must contain a JSON object.');

    const hasVersion = Object.prototype.hasOwnProperty.call(source, 'schemaVersion');
    if (hasVersion && source.schemaVersion !== 1) {
      throw new Error(`Schema version ${String(source.schemaVersion)} is not supported.`);
    }
    if (hasVersion && !object(source.project)) {
      throw new Error('Version 1 files must contain a project object.');
    }

    const input = hasVersion ? source.project : (object(source.project) ? source.project : source);
    if (!object(input)) throw new Error('The file does not contain a project object.');
    const project = JSON.parse(JSON.stringify(input));
    text(project.projectId, 128, 'Project ID', true);
    text(project.name, LIMITS.name, 'Project name', true);
    if (!['world-first', 'mechanics-first'].includes(project.approach)) {
      throw new Error('The approach must be world-first or mechanics-first.');
    }
    if (project.description === undefined) project.description = '';
    if (project.designGoals === undefined) project.designGoals = '';
    text(project.description, LIMITS.description, 'Project description');
    text(project.designGoals, LIMITS.designGoals, 'Design goals');
    if (project.starterPrompt !== undefined) text(project.starterPrompt, 2000, 'Starting prompt');
    if (!Array.isArray(project.cards) || !Array.isArray(project.relationships)) {
      throw new Error('Cards and relationships must be lists.');
    }
    if (project.cards.length > LIMITS.cards || project.relationships.length > LIMITS.relationships) {
      throw new Error('This project is larger than the supported import limit.');
    }
    if (project.customRelationshipLabels === undefined) project.customRelationshipLabels = [];
    if (!Array.isArray(project.customRelationshipLabels) || project.customRelationshipLabels.length > LIMITS.customRelationshipLabels) {
      throw new Error('Custom relationship labels must be a list of no more than 100 labels.');
    }

    const labels = new Map();
    for (const label of project.customRelationshipLabels) {
      text(label, LIMITS.relationshipLabel, 'Custom relationship label', true);
      const normalized = label.trim().toLocaleLowerCase();
      if (BUILTIN_LABELS.some(item => item.toLocaleLowerCase() === normalized) || labels.has(normalized)) {
        throw new Error('Custom relationship labels must be unique and cannot duplicate a built-in label.');
      }
      labels.set(normalized, label.trim());
    }

    const projectId = project.projectId;
    const cardIds = new Set();
    for (const card of project.cards) {
      if (!object(card)) throw new Error('Each card must be an object.');
      text(card.cardId, 128, 'Card ID', true);
      if (cardIds.has(card.cardId)) throw new Error('Card IDs must be unique.');
      cardIds.add(card.cardId);
      const normalizedType = TYPE_ALIASES[card.type] || card.type;
      if (!TYPES.includes(normalizedType)) throw new Error('Each card needs a supported type.');
      card.type = normalizedType;
      text(card.title, LIMITS.title, 'Card title', true);
      if (card.notes === undefined) card.notes = '';
      text(card.notes, LIMITS.notes, 'Card notes');
      if (card.projectId !== undefined && card.projectId !== projectId) {
        throw new Error('A card belongs to a different project.');
      }
      card.projectId = projectId;
      card.createdAt = stamp(card.createdAt);
      card.updatedAt = stamp(card.updatedAt);
    }

    const relationshipIds = new Set();
    for (const relationship of project.relationships) {
      if (!object(relationship)) throw new Error('Each relationship must be an object.');
      text(relationship.relationshipId, 128, 'Relationship ID', true);
      if (relationshipIds.has(relationship.relationshipId)) throw new Error('Relationship IDs must be unique.');
      relationshipIds.add(relationship.relationshipId);
      if (!cardIds.has(relationship.fromCardId) || !cardIds.has(relationship.toCardId)) {
        throw new Error('A connection refers to a missing card.');
      }
      if (relationship.fromCardId === relationship.toCardId) throw new Error('A card cannot be connected to itself.');
      text(relationship.label, LIMITS.relationshipLabel, 'Relationship label', true);
      if (!BUILTIN_LABELS.includes(relationship.label) && !labels.has(relationship.label.trim().toLocaleLowerCase())) {
        if (hasVersion) throw new Error('A connection uses an unknown relationship label.');
        if (labels.size >= LIMITS.customRelationshipLabels) throw new Error('Too many custom relationship labels.');
        labels.set(relationship.label.trim().toLocaleLowerCase(), relationship.label.trim());
      }
      if (relationship.projectId !== undefined && relationship.projectId !== projectId) {
        throw new Error('A connection belongs to a different project.');
      }
      relationship.projectId = projectId;
      relationship.createdAt = stamp(relationship.createdAt);
    }
    project.customRelationshipLabels = Array.from(labels.values());
    project.createdAt = stamp(project.createdAt);
    project.updatedAt = stamp(project.updatedAt);
    return project;
  }

  function makeExport(project) {
    const copy = JSON.parse(JSON.stringify(project));
    if (!Array.isArray(copy.customRelationshipLabels)) copy.customRelationshipLabels = [];
    copy.cards.forEach(card => { card.projectId = copy.projectId; });
    copy.relationships.forEach(relationship => { relationship.projectId = copy.projectId; });
    return { schemaVersion: 1, project: copy };
  }

  return { TYPES, TYPE_ALIASES, BUILTIN_LABELS, LIMITS, validateImport, makeExport };
});
