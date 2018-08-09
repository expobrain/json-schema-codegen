// @flow

export class Value {
  v: ?number;

  constructor(data: Object = {}) {
    this.v = data.v;
  }
}

export class Test {
  x: { [key: string]: Value };

  constructor(data: Object = {}) {
    this.x = Object.entries(data.x).reduce((acc, entry) => {
      const [key: string, value: Object] = (entry: any);
      const newValue = new Value(value);

      acc[key] = newValue;

      return acc;
    }, {});
  }
}
