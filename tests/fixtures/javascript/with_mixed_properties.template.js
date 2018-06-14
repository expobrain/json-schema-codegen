export class Test {
  id: number;
  name: ?string;

  constructor(data: Object = {}) {
    this.id = data.id;
    this.name = data.name;
  }
}
