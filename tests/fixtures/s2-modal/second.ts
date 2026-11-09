export class SecondDialog {
    order!: { id: string; active: boolean; lines: { id: string }[] };
    choice!: string;
    resolveWith!: (value?: unknown) => void;
    select() { this.resolveWith({ id: this.order.id, active: this.order.active, line: this.order.lines[0]?.id, choice: this.choice, kind: 'second' }); }
    cancel() { this.resolveWith(); }
}
