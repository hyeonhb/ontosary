import { Service } from './target';
export class Client { run(value: string) { return new Service().send(value); } }
