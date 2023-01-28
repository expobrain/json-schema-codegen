// @flow

declare type Value = {
  v: ?number,

  constructor(data: ?Object): void,
};

declare type Test = {
  x: { [key: string]: Value },

  constructor(data: ?Object): void,
};
