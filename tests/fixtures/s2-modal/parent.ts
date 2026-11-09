export class Parent {
    modal!: { fromComponent(component: unknown, options: unknown): { subscribe(next: (value: unknown) => void): void } };
    values: unknown[] = [];
    client!: { send(value: unknown): void };
    run(component: unknown, order: unknown) {
        this.modal.fromComponent(component, { locals: { order } }).subscribe(value => { this.values.push(value); if (value !== undefined) this.client.send(value); });
    }
}
