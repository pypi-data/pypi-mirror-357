import {BooleanField, booleanField} from "@web/views/fields/boolean/boolean_field";
import {onMounted, onRendered, useRef} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
const {document} = globalThis;

export class BooleanButton extends BooleanField {
    static template = "product_configurator.BooleanButtonField";

    setup() {
        super.setup();
        this.root = useRef("root");

        onMounted(() => {
            this.updateConfigurableButton();
        });

        onRendered(() => {
            this.updateConfigurableButton();
        });
    }

    updateConfigurableButton() {
        if (!this.root.el) {
            return;
        }
        this.text = this.state.value
            ? this.props.activeString
            : this.props.inactiveString;
        this.hover = this.state.value
            ? this.props.inactiveString
            : this.props.activeString;
        var val_color = this.state.value ? "text-success" : "text-danger";
        var hover_color = this.state.value ? "text-danger" : "text-success";

        const valSpan = document.createElement("span");
        valSpan.className = `o_stat_text o_boolean_button o_not_hover ${val_color}`;
        valSpan.textContent = this.text;

        const hoverSpan = document.createElement("span");
        hoverSpan.className = `o_stat_text o_boolean_button o_hover d-none ${hover_color}`;
        hoverSpan.textContent = this.hover;

        this.root.el.innerHTML = "";
        this.root.el.appendChild(valSpan);
        this.root.el.appendChild(hoverSpan);
    }
}

BooleanButton.props = {
    ...standardFieldProps,
    activeString: {type: String},
    inactiveString: {type: String, optional: true},
};

export const BooleanButtonField = {
    ...booleanField,
    component: BooleanButton,
    extractProps: ({options}) => {
        return {
            activeString: options.active,
            inactiveString: options.inactive,
        };
    },
};

// Register the field component
registry.category("fields").add("boolean_button", BooleanButtonField);
