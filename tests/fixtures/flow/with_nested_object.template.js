// @flow

declare type Nested = {
  x: ?string,

  constructor(data: ?Object): void
};

declare type Test = {
  nested: ?Nested,

  constructor(data: ?Object): void
};
