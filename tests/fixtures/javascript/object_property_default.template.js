export class Test {
  x: Object;

  constructor(data: Object = {}) {
    this.x = data.x !== null && typeof data.x === "object" ? data.x : { x: 42 };
  }
}
