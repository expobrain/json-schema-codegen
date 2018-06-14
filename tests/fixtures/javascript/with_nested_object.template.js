export class Nested {
  x: ?string;

  constructor(data: Object = {}) {
    this.x = data.x;
  }
}

export class Test {
  nested: ?Nested;

  constructor(data: Object = {}) {
    this.nested = data.nested;
  }
}
