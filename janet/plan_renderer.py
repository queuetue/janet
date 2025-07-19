from .phase_resource import PhaseResource


class PlanRenderer:
    def __init__(self, raw_planfile):
        # Support both old interface (single plan dict) and new interface (list of manifests)
        if isinstance(raw_planfile, dict) and "phases" in raw_planfile:
            # New YAML format with phases array
            self.phases = raw_planfile["phases"]
            self.all_resources = []
        elif isinstance(raw_planfile, dict) and "plan" in raw_planfile:
            # Old interface: single plan file
            self.plan_section = raw_planfile["plan"]
            self.all_resources = []
        elif isinstance(raw_planfile, list):
            # New interface: list of manifests
            try:
                self.plan_section = next(
                    doc["plan"] for doc in raw_planfile if isinstance(doc, dict) and "plan" in doc)
                self.all_resources = [doc for doc in raw_planfile if isinstance(
                    doc, dict) and "plan" not in doc]
            except StopIteration:
                raise ValueError("No plan document found in manifests")
        else:
            raise ValueError(
                "PlanRenderer expects either a plan dict or list of manifests")

    def render(self, target_phase=None):
        """Render plan into PMP-compliant Phase Manifest format."""
        result = []
        
        # Handle new phases array format (PMP-style)
        if hasattr(self, 'phases') and self.phases:
            for phase in self.phases:
                metadata = phase.get("metadata", {})
                spec = phase.get("spec", {})
                phase_id = metadata.get("name") or f"phase-{len(result)}"
                
                # Convert to PMP format
                pmp_phase = {
                    "Kind": "Phase",
                    "Id": phase_id,
                    "Spec": {
                        "description": spec.get("description", ""),
                        "selector": self._convert_selector_to_snake_case(spec.get("selector", {})),
                        "instance_mode": spec.get("instanceMode", "immediate"),
                        "wait_for": self._convert_wait_for_to_snake_case(spec.get("waitFor", {})),
                        "retry": spec.get("retry", {}),
                        "on_failure": spec.get("onFailure", {}),
                        "on_success": spec.get("onSuccess", {})
                    }
                }
                result.append(pmp_phase)
            return result
        
        # Handle legacy plan format
        plan = self.plan_section

        # Same as before
        if target_phase is None:
            target_phase = plan.get('targetPhase')
        default_mode = plan.get('defaultInstanceMode', 'immediate')

        phases = {
            k: v for k, v in plan.items()
            if k not in ['targetPhase', 'defaultInstanceMode'] and isinstance(v, dict)
        }

        ordered_phases = self._resolve_phase_order(phases, target_phase)

        for phase_name in ordered_phases:
            phase_config = phases[phase_name]
            instance_mode = phase_config.get('instanceMode', default_mode)

            # Create PMP-compliant phase
            spec = {
                'description': phase_config.get('description', ''),
                'selector': self._convert_selector_to_snake_case(phase_config.get('selector', {})),
                'instance_mode': instance_mode,
                'wait_for': self._convert_wait_for_to_snake_case(phase_config.get('waitFor', {})),
                'retry': phase_config.get('retry', {}),
                'on_failure': phase_config.get('onFailure', {}),
                'on_success': phase_config.get('onSuccess', {})
            }
            
            pmp_phase = {
                "Kind": "Phase",
                "Id": phase_name,
                "Spec": spec
            }
            result.append(pmp_phase)

            # NEW: apply selector to find matching resources
            selector = phase_config.get('selector', {})
            matched = self._select_resources(selector)
            result.extend(matched)

        return result

    def _select_resources(self, selector):
        """
        Return all resources matching the selector.
        For now, support matchLabels only.
        """
        match_labels = selector.get('matchLabels', {})
        if not match_labels:
            return []

        matches = []
        for resource in self.all_resources:
            labels = resource.get('metadata', {}).get('labels', {})
            if all(labels.get(k) == v for k, v in match_labels.items()):
                matches.append(resource)
        return matches

    def _resolve_phase_order(self, phases, target_phase=None):
        """
        Returns a list of phases in execution order,
        respecting waitFor dependencies, stopping at target_phase if given.

        Raises:
            ValueError if a circular dependency is detected
            ValueError if waitFor references unknown phases
        """
        visited = set()
        temp_visited = set()
        result = []

        def visit(phase_name):
            if phase_name in temp_visited:
                raise ValueError(
                    f"Circular dependency detected involving phase: {phase_name}")

            if phase_name in visited:
                return

            if phase_name not in phases:
                raise ValueError(f"Unknown phase referenced: {phase_name}")

            temp_visited.add(phase_name)
            wait_for = phases[phase_name].get('waitFor', {})
            depends_on = wait_for.get('dependsOn')
            if depends_on:
                if isinstance(depends_on, str):
                    depends_on = [depends_on]
                for dep in depends_on:
                    visit(dep)
            temp_visited.remove(phase_name)
            visited.add(phase_name)
            result.append(phase_name)
            if target_phase and phase_name == target_phase:
                raise StopIteration

        try:
            for phase in phases:
                visit(phase)
        except StopIteration:
            pass
        return result

    def _convert_selector_to_snake_case(self, selector):
        """Convert selector from camelCase to snake_case for PMP compatibility."""
        if not selector:
            return selector
        
        result = {}
        for key, value in selector.items():
            if key == "matchLabels":
                result["match_labels"] = value
            else:
                result[key] = value
        return result

    def _convert_wait_for_to_snake_case(self, wait_for):
        """Convert waitFor from camelCase to snake_case for PMP compatibility.""" 
        if not wait_for:
            return wait_for
        
        result = {}
        for key, value in wait_for.items():
            if key == "dependsOn":
                result["depends_on"] = value
            else:
                result[key] = value
        return result
