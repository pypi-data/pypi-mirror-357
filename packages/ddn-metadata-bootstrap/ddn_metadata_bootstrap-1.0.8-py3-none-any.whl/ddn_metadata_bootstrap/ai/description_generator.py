#!/usr/bin/env python3

"""
AI-powered description generation for schema elements.
Handles communication with Anthropic API and description quality control.
Enhanced to use explicit business context (use case + entity description) for meaningful descriptions.
"""

import logging
import re
from dataclasses import field
from typing import Dict, Set, Optional, Any, List

import anthropic
from markdown_it.rules_inline import entity

from ..config import config
from ..utils.text_utils import clean_description_response, refine_ai_description, normalize_description

logger = logging.getLogger(__name__)


class DescriptionGenerator:
    """Handles AI-powered description generation for schema elements."""

    def __init__(self, api_key: str, use_case: str, model: Optional[str] = None):
        """
        Initialize the description generator.

        Args:
            api_key: Anthropic API key
            model: Model to use (defaults to config value)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model or config.model
        self.use_case = use_case

    def generate_field_description(self, field_data: Dict, context: Dict) -> str:
        """
        Generate a description for a field using explicit business context.

        Args:
            field_data: Dictionary containing field information
            context: Context information including:
                - name: Entity name
                - kind: Entity kind
                - use_case: Explicit business use case (e.g., "Enterprise IT application portfolio management")
                - entity_description: What this entity represents (e.g., "Tracks applications deployed in the organization")

        Returns:
            Generated description or empty string if generation fails
        """
        field_name = field_data.get('name')
        if not field_name:
            return ""

        max_len = config.field_desc_max_length
        target_len = config.short_field_target
        parent_name = context.get('parent_name', '')
        parent_kind = context.get('ancestor_kind', '')
        field_type_formatted = self._format_type(field_data.get('type', field_data.get('outputType')))

        # Get explicit business context from caller
        use_case = context.get('use_case', self.use_case)
        entity_description = context.get('entity_description', '')

        # Extract semantic meaning using explicit context
        semantic_info = self._extract_field_semantics(field_name, parent_name, use_case, entity_description)

        # Log session start for monitoring
        logger.info(f"\n{'=' * 80}")
        logger.info(f"🎯 FIELD DESCRIPTION SESSION START")
        logger.info(f"   Target: {parent_name}.{field_name} ({field_type_formatted})")
        logger.info(f"   Context: {parent_kind} in schema")
        logger.info(f"   Use Case: {use_case}")
        if entity_description:
            logger.info(f"   Entity Description: {entity_description}")
        logger.info(f"   Limits: {max_len} chars max, {target_len} chars preferred")
        logger.info(f"{'=' * 80}")

        # Build context-aware prompt using explicit business context
        prompt = self._build_field_prompt(semantic_info, field_type_formatted, max_len)

        # Log the generation attempt for human monitoring
        logger.info(f"🔄 GENERATING FIELD DESCRIPTION")
        logger.info(f"   Field: '{field_name}' in '{parent_name}' ({parent_kind})")
        logger.info(f"   Use Case (explicit): {semantic_info['use_case']}")
        # logger.info(f"   Business Role: {semantic_info['business_role']}")
        if semantic_info.get('entity_description'):
            logger.info(f"   Entity Description: {semantic_info['entity_description']}")
        logger.info(f"   Business Context: {semantic_info['business_context']}")
        logger.info(f"   Prompt: {prompt}")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=config.field_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            desc = response.content[0].text.strip() if response and response.content else ""

            # Log raw AI response for monitoring
            logger.info(f"   Raw AI response: '{desc}'")

            desc = clean_description_response(desc)
            desc = refine_ai_description(desc)

            # Log processed description
            logger.info(f"   Processed: '{desc}' ({len(desc)} chars)")

            if (len(desc) <= max_len and
                    self._validate_description(desc, set(), "Field", field_name) and
                    len(desc.split()) >= 2):
                final_desc = normalize_description(desc, line_length=config.field_desc_max_length,
                                                   make_token_efficient=True)
                logger.info(f"✅ FIELD DESCRIPTION SUCCESS: '{final_desc}'")
                logger.info(
                    f"   Quality: Good | Length: {len(final_desc)}/{max_len} chars | Words: {len(final_desc.split())}")
                logger.info(f"{'=' * 80}")
                logger.info(f"🎉 SESSION COMPLETE: {parent_name}.{field_name} → SUCCESS")
                logger.info(f"{'=' * 80}\n")
                return final_desc

            # Try with shorter, more focused prompt if first attempt was too long
            logger.warning(f"⚠️  FIELD DESCRIPTION RETRY NEEDED")
            logger.warning(f"   Reason: Length {len(desc)} > {max_len} or validation failed")

            shorter_prompt = self._build_concise_field_prompt(semantic_info, field_type_formatted, target_len)
            logger.info(f"   Retry prompt: {shorter_prompt}")

            shorter_tokens = max(30, int(target_len / 2.5))
            response_short = self.client.messages.create(
                model=self.model,
                max_tokens=shorter_tokens,
                messages=[{"role": "user", "content": shorter_prompt}]
            )

            desc_short = response_short.content[0].text.strip() if response_short and response_short.content else ""
            logger.info(f"   Retry raw AI response: '{desc_short}'")

            desc_short = clean_description_response(desc_short)
            desc_short = refine_ai_description(desc_short)
            logger.info(f"   Retry processed: '{desc_short}' ({len(desc_short)} chars)")

            if (self._validate_description(desc_short, set(), "Field", field_name) and
                    desc_short and len(desc_short.split()) >= 2):
                final_desc_short = normalize_description(desc_short, line_length=config.field_desc_max_length,
                                                         make_token_efficient=True)
                logger.info(f"✅ FIELD DESCRIPTION RETRY SUCCESS: '{final_desc_short}'")
                logger.info(
                    f"   Quality: Acceptable | Length: {len(final_desc_short)}/{target_len} chars | Words: {len(final_desc_short.split())}")
                logger.info(f"{'=' * 80}")
                logger.info(f"🎉 SESSION COMPLETE: {parent_name}.{field_name} → RETRY SUCCESS")
                logger.info(f"{'=' * 80}\n")
                return final_desc_short
            else:
                logger.error(f"❌ FIELD DESCRIPTION RETRY FAILED")
                logger.error(f"   Both attempts failed for '{field_name}' in '{parent_name}'")
                final_fallback = (normalize_description(desc, line_length=config.field_desc_max_length,
                                                        make_token_efficient=True)
                                  if desc and self._validate_description(desc, set(), "Field", field_name)
                                     and len(desc.split()) >= 2 else "")
                if final_fallback:
                    logger.warning(f"⚠️  USING FALLBACK DESCRIPTION: '{final_fallback}'")
                    logger.warning(f"{'=' * 80}")
                    logger.warning(f"⚠️  SESSION COMPLETE: {parent_name}.{field_name} → FALLBACK")
                    logger.warning(f"{'=' * 80}\n")
                else:
                    logger.error(f"❌ NO DESCRIPTION GENERATED for '{field_name}'")
                    logger.error(f"{'=' * 80}")
                    logger.error(f"💥 SESSION COMPLETE: {parent_name}.{field_name} → FAILED")
                    logger.error(f"{'=' * 80}\n")
                return final_fallback

        except Exception as e:
            logger.error(f"❌ API ERROR for field '{field_name}' in '{parent_name}': {e}")
            logger.error(f"{'=' * 80}")
            logger.error(f"💥 SESSION COMPLETE: {parent_name}.{field_name} → API ERROR")
            logger.error(f"{'=' * 80}\n")
            return ""

    def generate_kind_description(self, data: Dict, context: Dict) -> str:
        """
        Generate a description for a schema kind using explicit business context.

        Args:
            data: Dictionary containing kind information
            context: Context information including:
                - name: Element name
                - kind: Element kind
                - use_case: Explicit business use case
                - entity_description: What this entity represents

        Returns:
            Generated description or empty string if generation fails
        """
        kind = context.get('kind')
        element_name = context.get('name')

        if not kind or not element_name:
            return ""

        max_len = config.kind_desc_max_length
        target_len = config.short_kind_target

        # Get explicit business context from caller
        use_case = self.use_case
        entity_description = context.get('entity_description', '')

        # Extract semantic meaning using explicit context
        # semantic_info = self._extract_element_semantics(element_name, kind, use_case, entity_description)

        # Log session start for monitoring
        logger.info(f"\n{'=' * 80}")
        logger.info(f"🎯 {kind.upper()} DESCRIPTION SESSION START")
        logger.info(f"   Target: {element_name} ({kind})")
        logger.info(f"   Use Case: {use_case}")
        if entity_description:
            logger.info(f"   Entity Description: {entity_description}")
        logger.info(f"   Limits: {max_len} chars max, {target_len} chars preferred")
        logger.info(f"{'=' * 80}")

        # Build context-aware prompt using explicit business context
        semantic_info = self._extract_element_semantics(element_name, kind, use_case, entity_description)
        prompt = self._build_kind_prompt(semantic_info, kind, max_len)

        # Log the generation attempt for human monitoring
        logger.info(f"🔄 GENERATING {kind.upper()} DESCRIPTION")
        logger.info(f"   Element: '{element_name}' ({kind})")
        logger.info(f"   Use Case (explicit): \"{use_case}\"")
        # logger.info(f"   Business Role: {semantic_info['business_role']}")
        # if semantic_info.get('entity_description'):
        #     logger.info(f"   Entity Description: {semantic_info['entity_description']}")
        logger.info(f"   Prompt: {prompt}")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=config.kind_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            desc = response.content[0].text.strip() if response and response.content else ""

            # Log raw AI response for monitoring
            logger.info(f"   Raw AI response: '{desc}'")

            desc = clean_description_response(desc)
            desc = refine_ai_description(desc)

            # Log processed description
            logger.info(f"   Processed: '{desc}' ({len(desc)} chars)")

            if (len(desc) <= max_len and
                    self._validate_description(desc, set(), kind, element_name)):
                final_desc = normalize_description(desc, line_length=config.line_length,
                                                   make_token_efficient=True)
                logger.info(f"✅ {kind.upper()} DESCRIPTION SUCCESS: '{final_desc}'")
                logger.info(
                    f"   Quality: Good | Length: {len(final_desc)}/{max_len} chars | Words: {len(final_desc.split())}")
                logger.info(f"{'=' * 80}")
                logger.info(f"🎉 SESSION COMPLETE: {element_name} ({kind}) → SUCCESS")
                logger.info(f"{'=' * 80}\n")
                return final_desc

            # Try with shorter, more focused prompt if first attempt was too long
            logger.warning(f"⚠️  {kind.upper()} DESCRIPTION RETRY NEEDED")
            logger.warning(f"   Reason: Length {len(desc)} > {max_len} or validation failed")

            shorter_prompt = self._build_concise_kind_prompt(semantic_info, kind, target_len)
            logger.info(f"   Retry prompt: {shorter_prompt}")

            shorter_tokens = max(50, int(target_len / 2))
            response_short = self.client.messages.create(
                model=self.model,
                max_tokens=shorter_tokens,
                messages=[{"role": "user", "content": shorter_prompt}]
            )

            desc_short = response_short.content[0].text.strip() if response_short and response_short.content else ""
            logger.info(f"   Retry raw AI response: '{desc_short}'")

            desc_short = clean_description_response(desc_short)
            desc_short = refine_ai_description(desc_short)
            logger.info(f"   Retry processed: '{desc_short}' ({len(desc_short)} chars)")

            if self._validate_description(desc_short, set(), kind, element_name) and desc_short:
                final_desc_short = normalize_description(desc_short, line_length=config.line_length,
                                                         make_token_efficient=True)
                logger.info(f"✅ {kind.upper()} DESCRIPTION RETRY SUCCESS: '{final_desc_short}'")
                logger.info(
                    f"   Quality: Acceptable | Length: {len(final_desc_short)}/{target_len} chars | Words: {len(final_desc_short.split())}")
                logger.info(f"{'=' * 80}")
                logger.info(f"🎉 SESSION COMPLETE: {element_name} ({kind}) → RETRY SUCCESS")
                logger.info(f"{'=' * 80}\n")
                return final_desc_short
            else:
                logger.error(f"❌ {kind.upper()} DESCRIPTION RETRY FAILED")
                logger.error(f"   Both attempts failed for '{element_name}' ({kind})")
                final_fallback = (normalize_description(desc, line_length=config.line_length,
                                                        make_token_efficient=True)
                                  if desc and self._validate_description(desc, set(), kind, element_name) else "")
                if final_fallback:
                    logger.warning(f"⚠️  USING FALLBACK DESCRIPTION: '{final_fallback}'")
                    logger.warning(f"{'=' * 80}")
                    logger.warning(f"⚠️  SESSION COMPLETE: {element_name} ({kind}) → FALLBACK")
                    logger.warning(f"{'=' * 80}\n")
                else:
                    logger.error(f"❌ NO DESCRIPTION GENERATED for '{element_name}' ({kind})")
                    logger.error(f"{'=' * 80}")
                    logger.error(f"💥 SESSION COMPLETE: {element_name} ({kind}) → FAILED")
                    logger.error(f"{'=' * 80}\n")
                return final_fallback

        except Exception as e:
            logger.error(f"❌ API ERROR for {kind} '{element_name}': {e}")
            logger.error(f"{'=' * 80}")
            logger.error(f"💥 SESSION COMPLETE: {element_name} ({kind}) → API ERROR")
            logger.error(f"{'=' * 80}\n")
            return ""

    def _extract_field_semantics(self, field_name: str, entity_name: str, use_case: str, entity_description: str) -> \
    Dict[str, Any]:
        """
        Extract business meaning using explicit use case + entity description + field analysis.

        Args:
            field_name: Field name in any case style
            entity_name: Name of the parent entity
            use_case: Explicit business use case (e.g., "Enterprise IT application portfolio management")
            entity_description: What the entity represents (e.g., "Tracks applications deployed in the organization")

        Returns:
            Dictionary with business-focused semantic information
        """
        if not field_name:
            return {
                "business_context": "general business information storage",
                "business_role": entity_description or "business entity",
                "use_case": use_case,
                "entity_description": entity_description
            }

        # Analyze field components
        components = self._split_field_name(field_name)

        # Detect technical patterns for classification
        is_identifier = self._is_identifier_field(components)
        is_reference = self._is_reference_field(components)
        is_status = self._is_status_field(components)
        is_count = self._is_count_field(components)
        is_timestamp = self._is_timestamp_field(components)
        is_flag = self._is_flag_field(components)

        # Use entity description as business role, or fall back to entity name analysis
        # business_role = entity_description or self._infer_business_role_from_name(entity_name, use_case)

        # Build business context using explicit context
        business_context = self._build_business_context_from_explicit_info(
            field_name, entity_name, components, '', use_case,
            is_identifier, is_reference, is_status, is_count, is_timestamp, is_flag
        )

        return {
            "business_context": business_context,
            # "business_role": business_role,
            "parent_name": entity_name,
            "name": field_name,
            "use_case": use_case,
            "entity_description": entity_description,
            "is_identifier": is_identifier,
            "is_reference": is_reference,
            "is_status": is_status,
            "is_count": is_count,
            "is_timestamp": is_timestamp,
            "is_flag": is_flag,
            "components": components
        }

    def _extract_element_semantics(self, element_name: str, kind: str, use_case: str, entity_description: str) -> Dict[
        str, Any]:
        """
        Extract business semantics for schema elements using explicit business context.

        Args:
            element_name: Element name
            kind: Element kind (ObjectType, Model, etc.)
            use_case: Explicit business use case
            entity_description: What the entity represents

        Returns:
            Dictionary with business-focused semantic information
        """
        # business_role = entity_description or self._infer_business_role_from_name(element_name, use_case)

        return {
            # "business_role": business_role,
            "name": element_name,
            "kind": kind,
            "use_case": use_case,
            "entity_description": entity_description
        }

    def _build_business_context_from_explicit_info(self, field_name: str, entity_name: str, components: List[str],
                                                   business_role: str, use_case: str,
                                                   is_identifier: bool, is_reference: bool, is_status: bool,
                                                   is_count: bool, is_timestamp: bool, is_flag: bool) -> str:
        """
        Build business context using explicit use case and entity description.

        Formula: EXPLICIT_USE_CASE + BUSINESS_ROLE + FIELD_PURPOSE = BUSINESS_CONTEXT
        """
        field_lower = field_name.lower()

        if is_flag:
            return self._build_flag_context(field_lower, business_role, use_case, entity_name)
        elif is_status:
            return f"current state of this {entity_name}"
        elif is_count:
            return self._build_count_context(field_lower, components, business_role, use_case, entity_name)
        elif is_timestamp:
            return self._build_timestamp_context(field_lower, components, business_role, use_case, entity_name)
        elif is_identifier and is_reference:
            return f"identifies another entity related to this {entity_name}"
        elif is_identifier:
            return f"unique identifier for this {entity_name}"
        elif is_reference:
            return f"connects this {entity_name} to another entity"
        else:
            return self._build_data_field_context(field_lower, components, business_role, use_case, entity_name)

    @staticmethod
    def _build_flag_context(field_lower: str, business_role: str, use_case: str, entity_name: str) -> str:
        """Build context for boolean flags."""
        flag_contexts = {
            'enabled': f"controls whether this {entity_name} is active and available",
            'active': f"indicates if this {entity_name} is currently operational",
            'available': f"shows whether this {entity_name} can be used",
            'deleted': f"tracks if this {entity_name} has been removed",
            'verified': f"confirms that this {entity_name} has been validated",
            'approved': f"shows whether this {entity_name} has received approval",
            'published': f"indicates if this {entity_name} is visible to users"
        }

        if field_lower.startswith('is_'):
            condition = field_lower[3:].replace('_', ' ')
            return f"indicates whether this {entity_name} is {condition}"
        elif field_lower.startswith('has_'):
            condition = field_lower[4:].replace('_', ' ')
            return f"shows whether this {entity_name} has {condition}"
        elif field_lower.startswith('can_'):
            condition = field_lower[4:].replace('_', ' ')
            return f"determines if this {entity_name} can {condition}"

        return flag_contexts.get(field_lower,
                                 f"business control flag for this {entity_name}")

    @staticmethod
    def _build_count_context(field_lower: str, components: List[str], business_role: str, use_case: str, entity_name) -> str:
        """Build context for count fields."""
        if any(comp in ['user', 'member', 'customer'] for comp in components):
            return f"number of users associated with {entity_name}"
        elif any(comp in ['service', 'application', 'app'] for comp in components):
            return f"count of applications or services connected to {entity_name}"
        else:
            return f"business metric counting {" ".join(components)} associated with {entity_name}"

    @staticmethod
    def _build_timestamp_context(field_lower: str, components: List[str], business_role: str,
                                 use_case: str, entity_name) -> str:
        """Build context for timestamp fields."""
        if any(comp in ['created', 'creation'] for comp in components):
            return f"when this {entity_name} was first created"
        elif any(comp in ['updated', 'modified', 'changed'] for comp in components):
            return f"when this {entity_name} was last modified"
        elif any(comp in ['found', 'discovered'] for comp in components):
            return f"when this {entity_name} was first identified"
        else:
            return f"timestamp tracking important events for this {entity_name}"

    @staticmethod
    def _build_data_field_context(field_lower: str, components: List[str], business_role: str,
                                  use_case: str, entity_name: str) -> str:
        """Build context for general data fields."""

        return f"business information about this {entity_name}"

    @staticmethod
    def _infer_business_role_from_name(entity_name: str, use_case: str) -> str:
        """Fallback: infer business role from entity name if no description provided."""
        if not entity_name:
            return "business entity"

        entity_lower = entity_name.lower()

        # Simple inference patterns
        if 'application' in entity_lower or 'app' in entity_lower:
            return "application or software system"
        elif 'user' in entity_lower:
            return "user account or person"
        elif 'company' in entity_lower or 'organization' in entity_lower:
            return "organization or business entity"
        elif 'order' in entity_lower:
            return "business order or transaction"

        return f"business entity"

    @staticmethod
    def _build_field_prompt(semantic_info: Dict[str, Any], field_type: str, max_len: int) -> str:
        """Build a business-focused prompt using explicit context."""
        business_context = semantic_info["business_context"]
        # use_case = semantic_info["use_case"]
        name = semantic_info["name"]

        # Build prompt focusing on business stakeholder perspective
        # context_explanation = f"In a {use_case} system, this field '{name}' {business_context}"

        # # Add type context only if it affects business understanding
        # type_hint = ""
        # if "Array" in field_type and not semantic_info.get("is_count"):
        #     type_hint = " (multiple values)"

        return f"Provide a business description (max {max_len} chars) for this field '{name}' of type '{field_type}' which {business_context}. YOU MOST NOT us the name of the field, the type of the field, or the use case, in your description. Always begin with a verb."

    @staticmethod
    def _build_concise_field_prompt(semantic_info: Dict[str, Any], field_type, target_len: int) -> str:
        business_context = semantic_info["business_context"]
        # use_case = semantic_info["use_case"]
        name = semantic_info["name"]

        # Build prompt focusing on business stakeholder perspective
        # context_explanation = f"In a {use_case} system, this field '{name}' {business_context}"

        # # Add type context only if it affects business understanding
        # type_hint = ""
        # if "Array" in field_type and not semantic_info.get("is_count"):
        #     type_hint = " (multiple values)"

        return f"Provide a concise business description which cannot exceed {target_len} chars) for this field '{name}' of type '{field_type}' which {business_context}. YOU MOST NOT us the name of the field, the type of the field, or the use case, in your description. Always begin with a verb."

    @staticmethod
    def _build_kind_prompt(semantic_info: Dict[str, Any], kind: str, max_len: int) -> str:
        """Build a business-focused prompt for entity descriptions."""
        use_case = semantic_info["use_case"]
        # business_role = semantic_info["business_role"]
        name = semantic_info["name"]
        entity_description = semantic_info["entity_description"]

        # Focus on business purpose and stakeholder value
        if kind == "ObjectType":
            if entity_description:
                context = f"In a {use_case} system, this data structure named: '{name}' which is described as: '{entity_description}'"
            else:
                context = f"In a {use_case} system, this data structure named: '{name}'"
        elif kind == "Model":
            context = f"In a {use_case} system, this API model provides access to {name}"
        else:
            context = f"In a {use_case} system, this component supports {name}"

        return f"Business description (max {max_len} chars): {context}. Explain the purpose, in terms that a business analyst might use, of this within the {use_case}."

    @staticmethod
    def _build_concise_kind_prompt(semantic_info: Dict[str, Any], kind: str, target_len: int) -> str:
        """Build a concise business-focused prompt for entity descriptions."""
        use_case = semantic_info["use_case"]
        name  = semantic_info["name"]

        if kind == "ObjectType" or kind == "Model":
            return f"Concise business description (max {target_len} chars) of a data entity named '{name}' used within the {use_case}."
        return f"Concise business description (max {target_len} chars) of a data field named '{name}' used within the {use_case}."


    @staticmethod
    def _split_field_name(field_name: str) -> List[str]:
        """Split field name into semantic components across case styles."""
        if '_' in field_name:
            return [part.lower() for part in field_name.split('_') if part]

        # Handle camelCase and PascalCase
        spaced = re.sub(r'(?<!^)(?=[A-Z])', '_', field_name)
        return [part.lower() for part in spaced.split('_') if part]

    @staticmethod
    def _is_identifier_field(components: List[str]) -> bool:
        """Check if field represents an identifier."""
        id_patterns = {'id', 'identifier', 'key', 'uid', 'uuid', 'guid', 'pk'}
        return any(comp in id_patterns for comp in components)

    def _is_reference_field(self, components: List[str]) -> bool:
        """Check if field represents a reference to another entity."""
        ref_patterns = {'ref', 'reference', 'fk', 'foreign', 'link'}
        return (any(comp in ref_patterns for comp in components) or
                (self._is_identifier_field(components) and len(components) > 1))

    @staticmethod
    def _is_status_field(components: List[str]) -> bool:
        """Check if field represents status information."""
        status_patterns = {'status', 'state', 'condition', 'phase', 'stage'}
        return any(comp in status_patterns for comp in components)

    @staticmethod
    def _is_count_field(components: List[str]) -> bool:
        """Check if field represents a count or quantity."""
        count_patterns = {'count', 'total', 'num', 'number', 'quantity', 'amount', 'size'}
        return any(comp in count_patterns for comp in components)

    @staticmethod
    def _is_timestamp_field(components: List[str]) -> bool:
        """Check if field represents timestamp information."""
        time_patterns = {'created', 'updated', 'modified', 'deleted', 'at', 'time', 'date', 'timestamp', 'when',
                         'found'}
        return any(comp in time_patterns for comp in components)

    @staticmethod
    def _is_flag_field(components: List[str]) -> bool:
        """Check if field represents a boolean flag."""
        flag_patterns = {'is', 'has', 'can', 'should', 'will', 'enabled', 'disabled', 'active', 'inactive', 'verified',
                         'approved'}
        return any(comp in flag_patterns for comp in components)

    @staticmethod
    def _format_type(type_str: Any) -> str:
        """Format type information for display."""
        if not type_str or not isinstance(type_str, str):
            return "UnknownType"

        is_nullable = not type_str.endswith('!')
        base_type = type_str.rstrip('!')

        if base_type.startswith('[') and base_type.endswith(']'):
            inner = base_type[1:-1].rstrip('!')
            return f"Array of {inner} ({'nullable' if is_nullable else 'non-nullable'})"

        return f"{base_type} ({'nullable' if is_nullable else 'non-nullable'})"

    @staticmethod
    def _validate_description(description: str, domain_keywords: Set[str], kind: str, name: str) -> bool:
        """Validate that a description meets basic quality criteria."""
        if not description or not description.strip():
            return False

        # Check for common redundant patterns
        redundant_patterns = [
            f"the {name.lower()}",
            f"this {name.lower()}",
            f"{name.lower()} field",
            "here are some options",
            "this field represents"
        ]

        desc_lower = description.lower()
        for pattern in redundant_patterns:
            if pattern in desc_lower:
                logger.debug(f"Description contains potentially redundant pattern '{pattern}': {description}")

        return True
