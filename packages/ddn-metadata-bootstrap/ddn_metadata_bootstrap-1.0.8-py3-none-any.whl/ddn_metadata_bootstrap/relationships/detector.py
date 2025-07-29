#!/usr/bin/env python3

"""
Relationship detection logic for identifying connections between schema entities.
Analyzes foreign keys, shared fields, and naming patterns to detect relationships.
Only detects relationships between ObjectTypes that have associated Models.

Key improvements:
- Minimum confidence threshold to prevent spurious FK relationships
- camelCase to snake_case conversion for comprehensive field analysis (analysis only)
- Always preserves original field names in relationship data
"""

import logging
import re
from typing import Dict, List, Set, Optional, Tuple, Any

from ..config import config

logger = logging.getLogger(__name__)


class RelationshipDetector:
    """
    Detects relationships between schema entities through various analysis methods.

    This class implements multiple detection strategies:
    - Foreign key template matching with confidence thresholds
    - Shared field analysis with camelCase support
    - Naming pattern recognition
    - Domain-specific relationship hints

    Only creates relationships between ObjectTypes that have associated Models.
    """

    def __init__(self):
        """Initialize the relationship detector with parsed templates."""
        self.parsed_fk_templates = self._parse_fk_templates()
        self.generic_fields_lower = [gf.lower() for gf in config.generic_fields]
        self.domain_identifiers = config.domain_identifiers

        # Minimum confidence score for FK relationships to prevent spurious matches
        self.min_confidence_score = 50

        logger.info(
            f"Initialized RelationshipDetector with {len(self.generic_fields_lower)} generic fields for FK suffix matching: "
            f"{', '.join(self.generic_fields_lower)}")
        logger.info(f"Minimum FK confidence threshold: {self.min_confidence_score}")

    @staticmethod
    def _camel_to_snake_case(field_name: str) -> str:
        """
        Convert camelCase field names to snake_case for analysis only.

        Examples:
        - lastUsedFileName → last_used_file_name
        - userId → user_id
        - companyId → company_id
        - XMLHttpRequest → xml_http_request

        Args:
            field_name: Original field name (may be camelCase or snake_case)

        Returns:
            snake_case version of the field name
        """
        if not field_name:
            return field_name

        # If already contains underscores, likely already snake_case
        if '_' in field_name:
            return field_name.lower()

        # Handle sequences of capitals (like XMLHttp → xml_http)
        # Insert underscore before capitals that follow lowercase or are followed by lowercase
        snake_case = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', field_name)
        snake_case = re.sub(r'([A-Z])([A-Z][a-z])', r'\1_\2', snake_case)

        # Convert to lowercase and remove any leading underscores
        return snake_case.lower().lstrip('_')

    @staticmethod
    def _is_relationship_worthy_type(field_type: str) -> bool:
        """
        Determine if a field type supports relationships based on data connector equality operators.

        Only string, int, long, bigint types have equality operators and make sense for relationships.

        Args:
            field_type: The type declaration from the field definition

        Returns:
            True if field type supports relationships
        """
        if not field_type:
            return False

        # Skip arrays (start with '[')
        if field_type.startswith('['):
            logger.debug(f"Field type '{field_type}' is array - excluding from relationships")
            return False

        # Extract base type (ignore case, !, _numbers)
        base_type = re.sub(r'[!_\d]+$', '', field_type).lower()

        # Only these specific primitive types support meaningful relationships
        allowed_types = {'string', 'int', 'long', 'bigint'}

        is_allowed = base_type in allowed_types

        if not is_allowed:
            logger.debug(f"Field type '{field_type}' -> base '{base_type}' not in allowed types {allowed_types}")

        return is_allowed

    def detect_foreign_key_relationships(self, entities_map: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Detect foreign key relationships using template matching.

        Uses templates like {primary_table}_{generic_id} to identify FK patterns.
        Now includes camelCase to snake_case conversion for analysis and minimum confidence thresholds.
        Always preserves original field names in returned relationship data.

        Only detects relationships between ObjectTypes that have associated Models.

        Args:
            entities_map: Dictionary mapping qualified entity names to entity info

        Returns:
            List of detected foreign key relationships with original field names preserved
        """
        relationships = []

        # Filter entities to only include those with associated Models
        model_entities_map = self._filter_entities_with_models(entities_map)

        logger.info(f"Analyzing {len(model_entities_map)} entities with Models for foreign key relationships "
                    f"(filtered from {len(entities_map)} total entities)")
        logger.info(f"Using camelCase→snake_case conversion for analysis only - preserving original field names")
        logger.info(f"Minimum confidence threshold: {self.min_confidence_score}")

        for source_qnk, source_info in model_entities_map.items():
            source_subgraph = source_info.get('subgraph')
            # Convert primary keys to snake_case for comparison
            source_pks = {self._camel_to_snake_case(pk) for pk in source_info.get('primary_keys', [])}

            for field in source_info.get('fields', []):
                field_name = field.get('name', '')
                field_type = field.get('type', '')

                if not field_name:
                    continue

                # Convert to snake_case ONLY for analysis - preserve original field_name
                field_name_snake = self._camel_to_snake_case(field_name)

                # Skip primary keys using snake_case comparison
                if field_name_snake in source_pks:
                    logger.debug(f"Skipping primary key field '{field_name}' in {source_qnk} for FK detection")
                    continue

                # Check if this field type supports relationships
                if not self._is_relationship_worthy_type(field_type):
                    logger.debug(
                        f"Skipping field '{field_name}' with type '{field_type}' in {source_qnk} - not relationship-worthy")
                    continue

                # Try each FK template against the snake_case version for matching
                for template_info in self.parsed_fk_templates:
                    fk_regex = template_info['fk_regex']
                    pk_template_str = template_info['pk_template_str']

                    match = fk_regex.match(field_name_snake)
                    if match:
                        relationship = self._process_fk_template_match(
                            match, source_qnk, source_info, field_name, pk_template_str, model_entities_map
                        )
                        if relationship:
                            relationships.append(relationship)
                            break  # Stop after first successful template match

        logger.info(f"Detected {len(relationships)} foreign key relationships between entities with Models")
        return relationships

    def detect_shared_field_relationships(self, entities_map: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Detect relationships based on shared field names.

        Uses camelCase to snake_case conversion for analysis but preserves original field names.
        Only detects relationships between ObjectTypes that have associated Models.

        Args:
            entities_map: Dictionary mapping qualified entity names to entity info

        Returns:
            List of detected shared field relationships with original field names preserved
        """
        relationships = []

        # Filter entities to only include those with associated Models
        model_entities_map = self._filter_entities_with_models(entities_map)

        logger.info(f"Analyzing {len(model_entities_map)} entities with Models for shared field relationships "
                    f"(filtered from {len(entities_map)} total entities)")
        logger.info(f"Using camelCase→snake_case conversion for comparison only - preserving original field names")

        # Build field mapping: snake_case → {original_name, entity_qnk}
        snake_case_field_map = {}

        for qnk, info in model_entities_map.items():
            for f in info.get('fields', []):
                field_name = f.get('name')
                field_type = f.get('type', '')
                if field_name and self._is_relationship_worthy_type(field_type):
                    field_name_snake = self._camel_to_snake_case(field_name)

                    if field_name_snake not in snake_case_field_map:
                        snake_case_field_map[field_name_snake] = []

                    snake_case_field_map[field_name_snake].append({
                        'entity_qnk': qnk,
                        'original_field_name': field_name
                    })

        # Find shared fields (snake_case fields that appear in multiple entities)
        for field_snake, field_instances in snake_case_field_map.items():
            if len(field_instances) < 2:
                continue  # Not shared

            # Skip generic fields and primary keys using snake_case comparison
            if field_snake in self.generic_fields_lower:
                logger.debug(f"Skipping generic field '{field_snake}' for shared field relationships")
                continue

            # Check all pairs of entities that share this field
            for i, instance1 in enumerate(field_instances):
                for instance2 in field_instances[i + 1:]:
                    qnk1 = instance1['entity_qnk']
                    qnk2 = instance2['entity_qnk']

                    entity1_info = model_entities_map[qnk1]
                    entity2_info = model_entities_map[qnk2]

                    # Skip if either entity has this field as primary key
                    entity1_pks = {self._camel_to_snake_case(pk) for pk in entity1_info.get('primary_keys', [])}
                    entity2_pks = {self._camel_to_snake_case(pk) for pk in entity2_info.get('primary_keys', [])}

                    if field_snake in entity1_pks or field_snake in entity2_pks:
                        logger.debug(
                            f"Skipping shared field '{field_snake}' between {qnk1} and {qnk2} - is primary key")
                        continue

                    # Create shared field relationship
                    confidence = self._calculate_shared_field_confidence(field_snake)

                    relationship = {
                        'from_entity': qnk1,
                        'to_entity': qnk2,
                        'shared_field': field_snake,  # snake_case for processing consistency
                        'original_field1': instance1['original_field_name'],  # PRESERVE original
                        'original_field2': instance2['original_field_name'],  # PRESERVE original
                        'relationship_type': 'shared_field',
                        'confidence': confidence,
                        'cross_subgraph': entity1_info.get('subgraph') != entity2_info.get('subgraph')
                    }

                    relationships.append(relationship)

        logger.info(f"Detected {len(relationships)} shared field relationships between entities with Models")
        return relationships

    def detect_naming_pattern_relationships(self, entities_map: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Detect relationships based on naming patterns and conventions.

        Only detects relationships between ObjectTypes that have associated Models.

        Args:
            entities_map: Dictionary mapping qualified entity names to entity info

        Returns:
            List of detected naming pattern relationships
        """
        relationships = []

        # Filter entities to only include those with associated Models
        model_entities_map = self._filter_entities_with_models(entities_map)

        logger.info(f"Analyzing {len(model_entities_map)} entities with Models for naming pattern relationships "
                    f"(filtered from {len(entities_map)} total entities)")

        # Analyze entity names for hierarchical patterns
        entity_names = [(qnk, info.get('name', '')) for qnk, info in model_entities_map.items()]

        for qnk1, name1 in entity_names:
            for qnk2, name2 in entity_names:
                if qnk1 >= qnk2 or not name1 or not name2:
                    continue

                pattern_relationship = self._analyze_naming_patterns(qnk1, name1, qnk2, name2, model_entities_map)
                if pattern_relationship:
                    relationships.append(pattern_relationship)

        logger.info(f"Detected {len(relationships)} naming pattern relationships between entities with Models")
        return relationships

    def find_referenced_entity(self, ref_entity_name_guess: str,
                               explicit_target_subgraph: Optional[str],
                               source_entity_qnk: str, entities_map: Dict[str, Dict],
                               source_entity_subgraph: Optional[str]) -> Optional[str]:
        """
        Find the best matching entity for a reference guess.

        Now includes minimum confidence threshold to reject weak matches.
        Only considers entities that have associated Models.

        Args:
            ref_entity_name_guess: Guessed entity name from field analysis
            explicit_target_subgraph: Explicit subgraph hint from template
            source_entity_qnk: Qualified name of source entity
            entities_map: Map of all entities
            source_entity_subgraph: Subgraph of source entity

        Returns:
            Qualified name of best matching target entity or None
        """
        if not ref_entity_name_guess:
            return None

        ref_lower = ref_entity_name_guess.lower()
        possible_targets = []

        for target_qnk, target_info in entities_map.items():
            # Skip entities without associated Models
            if not target_info.get('has_associated_model', False):
                continue

            target_name = target_info.get('name', '')
            if not target_name:
                continue

            target_name_lower = target_name.lower()
            target_subgraph = target_info.get('subgraph')
            target_kind = target_info.get('kind')

            score, match_details = self._calculate_entity_match_score(
                ref_lower, target_name_lower, target_subgraph, target_kind,
                explicit_target_subgraph, source_entity_subgraph
            )

            if score > 0:
                possible_targets.append({
                    'qnk': target_qnk,
                    'score': score,
                    'match_details': match_details
                })

        if not possible_targets:
            return None

        # Return the highest scoring match only if it meets minimum confidence threshold
        possible_targets.sort(key=lambda t: t['score'], reverse=True)
        best_match = possible_targets[0]

        # Apply minimum confidence threshold to prevent spurious relationships
        if best_match['score'] < self.min_confidence_score:
            logger.debug(f"Rejecting weak match for '{ref_entity_name_guess}': "
                         f"best score {best_match['score']} < {self.min_confidence_score} "
                         f"(target: {best_match['qnk']}, details: {best_match['match_details']})")
            return None

        logger.debug(f"Accepted match for '{ref_entity_name_guess}': {best_match['qnk']} "
                     f"(score: {best_match['score']}, details: {best_match['match_details']})")

        return best_match['qnk']

    def scan_for_existing_relationships(self, file_paths: List[str]) -> Set[Tuple]:
        """
        Scan files for existing relationship definitions to avoid duplicates.

        Args:
            file_paths: List of file paths to scan

        Returns:
            Set of relationship signatures (source_type, canonical_mapping)
        """
        from ..utils.yaml_utils import load_yaml_documents

        existing_signatures = set()

        logger.info(f"Scanning {len(file_paths)} files for existing relationships...")

        for file_path in file_paths:
            try:
                documents = load_yaml_documents(file_path)
                for doc in documents:
                    if isinstance(doc, dict) and doc.get('kind') == 'Relationship':
                        signature = self._extract_relationship_signature(doc)
                        if signature:
                            existing_signatures.add(signature)
            except Exception as e:
                logger.error(f"Error scanning file {file_path} for existing relationships: {e}")

        logger.info(f"Found {len(existing_signatures)} existing relationship signatures")
        return existing_signatures

    @staticmethod
    def _filter_entities_with_models(entities_map: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Filter entities to only include those with associated Models.

        Args:
            entities_map: Dictionary mapping qualified entity names to entity info

        Returns:
            Filtered dictionary containing only entities with associated Models
        """
        model_entities = {}

        for qnk, entity_info in entities_map.items():
            if entity_info.get('has_associated_model', False):
                model_entities[qnk] = entity_info
            else:
                logger.debug(f"Excluding entity {qnk} from relationship detection - no associated Model")

        logger.info(f"Filtered {len(entities_map)} entities to {len(model_entities)} entities with Models")
        return model_entities

    @staticmethod
    def _parse_fk_templates() -> List[Dict]:
        """Parse foreign key templates from configuration."""
        parsed_templates = []

        if not config.fk_templates_string:
            logger.warning("No FK templates string provided.")
            return parsed_templates

        template_pairs = config.fk_templates_string.split(',')

        # Build regex patterns
        pt_re = r"(?P<primary_table>\w+?)"
        ps_re = r"(?P<primary_subgraph>\w+?)"
        fs_re = r"(?P<foreign_subgraph>\w+?)"

        sorted_generic_fields = sorted(config.generic_fields, key=len, reverse=True)
        gi_re_options = "|".join(re.escape(gf) for gf in sorted_generic_fields)
        gi_re = f"(?P<generic_id>(?:{gi_re_options}))"

        for tpl_pair_str in template_pairs:
            tpl_pair_str = tpl_pair_str.strip()
            if not tpl_pair_str or '|' not in tpl_pair_str:
                continue

            pk_tpl_str, fk_tpl_str_orig = [part.strip() for part in tpl_pair_str.split('|', 1)]

            # Build regex pattern
            fk_regex_str = fk_tpl_str_orig
            fk_regex_str = fk_regex_str.replace("{fs}", fs_re)
            fk_regex_str = fk_regex_str.replace("{ps}", ps_re)
            fk_regex_str = fk_regex_str.replace("{pt}", pt_re)
            fk_regex_str = fk_regex_str.replace("{gi}", gi_re)
            fk_regex_str = f"^{fk_regex_str}$"

            try:
                compiled_regex = re.compile(fk_regex_str)
                parsed_templates.append({
                    'pk_template_str': pk_tpl_str,
                    'fk_template_str_orig': fk_tpl_str_orig,
                    'fk_regex': compiled_regex
                })
                logger.debug(f"Parsed FK template: PK='{pk_tpl_str}', FK='{fk_tpl_str_orig}'")
            except re.error as e:
                logger.error(f"Failed to compile regex for FK template '{fk_tpl_str_orig}': {e}")

        return parsed_templates

    def _process_fk_template_match(self, match, source_qnk: str, source_info: Dict,
                                   field_name: str, pk_template_str: str,
                                   entities_map: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
        """Process a successful foreign key template match."""
        match_groups = match.groupdict()
        guessed_primary_table = match_groups.get('primary_table')
        guessed_generic_id = match_groups.get('generic_id')
        explicit_target_subgraph = match_groups.get('primary_subgraph')
        source_subgraph = source_info.get('subgraph')

        if not guessed_primary_table:
            return None

        # Generate entity name variations to check
        forms_to_check = {guessed_primary_table.lower()}
        if guessed_primary_table.lower().endswith('s') and len(guessed_primary_table) > 1:
            forms_to_check.add(guessed_primary_table.lower()[:-1])  # Singular
        else:
            forms_to_check.add(guessed_primary_table.lower() + 's')  # Plural

        forms_to_check.discard("")  # Remove empty strings

        # Find best matching target entity
        for form in forms_to_check:
            target_qnk = self.find_referenced_entity(
                form, explicit_target_subgraph, source_qnk, entities_map, source_subgraph
            )

            if target_qnk and target_qnk != source_qnk:
                target_info = entities_map.get(target_qnk, {})

                # Additional check: Ensure target has associated Model
                if not target_info.get('has_associated_model', False):
                    logger.debug(
                        f"Skipping relationship from {source_qnk}.{field_name} to {target_qnk} - target has no associated Model")
                    continue

                # Determine target field name AND VALIDATE IT EXISTS
                to_field_name = self._determine_and_validate_target_field_name(
                    pk_template_str, guessed_generic_id, target_info
                )

                # Only create relationship if target field actually exists
                if not to_field_name:
                    logger.debug(
                        f"Skipping relationship from {source_qnk}.{field_name} to {target_qnk} - no valid target field found")
                    continue

                return {
                    'from_entity': source_qnk,
                    'from_field': field_name,  # PRESERVE original field name (camelCase or snake_case)
                    'to_entity': target_qnk,
                    'to_field_name': to_field_name,  # PRESERVE original target field name
                    'relationship_type': 'foreign_key_template',
                    'confidence': 'high',
                    'cross_subgraph': source_subgraph != target_info.get('subgraph'),
                    'template_used': pk_template_str
                }

        return None

    @staticmethod
    def _calculate_entity_match_score(ref_name: str, target_name: str,
                                      target_subgraph: Optional[str], target_kind: str,
                                      explicit_subgraph: Optional[str],
                                      source_subgraph: Optional[str]) -> Tuple[int, str]:
        """Calculate matching score between reference and target entity."""
        score = 0
        match_details = []

        # Direct name match
        if target_name == ref_name:
            score += 15
            match_details.append("exact_name")

        # Prefix match (subgraph_entityname pattern)
        elif target_name.endswith(f"_{ref_name}"):
            potential_prefix = target_name[:-len(f"_{ref_name}")]
            score += 12
            match_details.append("prefix_match")

            # Bonus if prefix matches target's subgraph
            if target_subgraph and potential_prefix == target_subgraph.lower():
                score += 10
                match_details.append("prefix_matches_subgraph")

            # Bonus if prefix matches source's subgraph
            if source_subgraph and potential_prefix == source_subgraph.lower():
                score += 25
                match_details.append("prefix_matches_source_subgraph")

        # Plural/singular variations
        if len(ref_name) > 1:
            if target_name == ref_name + "s":
                score = max(score, 9)
                if not match_details:
                    match_details.append("plural_target")
            elif target_name + "s" == ref_name:
                score = max(score, 7)
                if not match_details:
                    match_details.append("plural_reference")

        # Subgraph bonuses
        if score > 0:
            if explicit_subgraph and target_subgraph and explicit_subgraph.lower() == target_subgraph.lower():
                score += 200
                match_details.append("EXPLICIT_SUBGRAPH_MATCH")
            elif source_subgraph and target_subgraph == source_subgraph:
                score += 100
                match_details.append("SAME_SUBGRAPH")

        # Kind bonuses
        if target_kind == 'ObjectType':
            score += 20
        elif target_kind == 'Model':
            score += 10

        return score, ", ".join(match_details)

    @staticmethod
    def _determine_and_validate_target_field_name(pk_template: str, guessed_generic_id: Optional[str],
                                                  target_info: Dict) -> Optional[str]:
        """
        Determine the target field name for a relationship AND validate it exists in the target entity.

        Args:
            pk_template: Primary key template from configuration
            guessed_generic_id: Guessed generic identifier from field matching
            target_info: Target entity information

        Returns:
            Valid target field name if found, None if no valid field exists
        """
        # Get the list of actual field names in the target entity
        target_field_names = {f.get('name', '').lower() for f in target_info.get('fields', []) if f.get('name')}
        target_pks = target_info.get('primary_keys', [])

        # List of candidate field names to check, in order of preference
        candidate_fields = []

        # 1. If template specifies a generic ID and we have one, try it first
        if pk_template == "{gi}" and guessed_generic_id:
            candidate_fields.append(guessed_generic_id.lower())

        # 2. If template specifies a literal field name, try it
        elif pk_template and pk_template != "{gi}":
            candidate_fields.append(pk_template.lower())

        # 3. Try primary keys (these are always valid targets even if generic)
        for pk in target_pks:
            candidate_fields.append(pk.lower())

        # 4. Try common ID field names
        candidate_fields.extend(['_id', 'id', 'key', '_key', 'identifier', 'uid', 'uuid'])

        # 5. If we have a guessed generic ID, try it as fallback
        if guessed_generic_id and guessed_generic_id.lower() not in candidate_fields:
            candidate_fields.append(guessed_generic_id.lower())

        # Check each candidate field to see if it actually exists in the target entity
        for candidate in candidate_fields:
            if candidate in target_field_names:
                # Return the original case version
                for field in target_info.get('fields', []):
                    if field.get('name', '').lower() == candidate:
                        logger.debug(f"Found valid target field: {field.get('name')}")
                        return field.get('name')  # PRESERVE original case

        # If no valid field found, log a warning and return None
        available_fields = [f.get('name') for f in target_info.get('fields', []) if f.get('name')]
        logger.warning(f"No valid target field found for entity {target_info.get('name', 'unknown')}. "
                       f"Tried: {candidate_fields}, Available: {available_fields}")
        return None

    def _calculate_shared_field_confidence(self, field_name: str) -> str:
        """Calculate confidence level for shared field relationships."""
        if any(domain_id in field_name for domain_id in self.domain_identifiers):
            return 'medium'
        return 'low'

    @staticmethod
    def _is_hierarchical_naming(name1: str, name2: str) -> bool:
        """Check if two names follow a hierarchical pattern."""
        # Simple patterns: one name contains the other
        return (name1 in name2 and name1 != name2) or (name2 in name1 and name1 != name2)

    def _analyze_naming_patterns(self, qnk1: str, name1: str, qnk2: str, name2: str,
                                 entities_map: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
        """Analyze naming patterns between two entities."""
        entity1_info = entities_map[qnk1]
        entity2_info = entities_map[qnk2]

        # Additional check: Both entities must have associated Models
        if not (entity1_info.get('has_associated_model', False) and entity2_info.get('has_associated_model', False)):
            logger.debug(
                f"Skipping naming pattern analysis between {qnk1} and {qnk2} - one or both lack associated Models")
            return None

        name1_lower = name1.lower()
        name2_lower = name2.lower()

        # Check for hierarchical patterns (parent-child naming)
        if self._is_hierarchical_naming(name1_lower, name2_lower):
            return {
                'from_entity': qnk1,
                'to_entity': qnk2,
                'relationship_type': 'naming_hierarchy',
                'confidence': 'medium',
                'cross_subgraph': entity1_info.get('subgraph') != entity2_info.get('subgraph'),
                'pattern_type': 'hierarchical_naming'
            }

        return None

    @staticmethod
    def _extract_relationship_signature(relationship_doc: Dict) -> Optional[Tuple]:
        """Extract a signature from an existing relationship document."""
        try:
            definition = relationship_doc.get('definition', {})
            source_type = definition.get('sourceType')
            mapping = definition.get('mapping', [])

            if not source_type or not mapping:
                return None

            canonical_mapping_parts = []
            for m_item in mapping:
                if isinstance(m_item, dict):
                    source_fp = m_item.get('source', {}).get('fieldPath', [])
                    target_block = m_item.get('target', {})
                    target_fp = target_block.get('modelField', target_block.get('fieldPath', []))

                    # Convert to tuples for hashing
                    source_tuple = tuple(fp.get('fieldName', fp) if isinstance(fp, dict) else fp for fp in source_fp)
                    target_tuple = tuple(fp.get('fieldName', fp) if isinstance(fp, dict) else fp for fp in target_fp)

                    canonical_mapping_parts.append((source_tuple, target_tuple))

            canonical_mapping_parts.sort()
            return source_type, frozenset(canonical_mapping_parts)

        except Exception as e:
            logger.warning(f"Could not extract signature from relationship: {e}")
            return None


def create_relationship_detector() -> RelationshipDetector:
    """
    Create a RelationshipDetector instance.

    Returns:
        Configured RelationshipDetector instance
    """
    return RelationshipDetector()
