import { a as patchEsm, b as bootstrapLazy } from './core-692256d4.js';

const defineCustomElements = (win, options) => {
  return patchEsm().then(() => {
    bootstrapLazy([["lwc-limepkg-scrive",[[0,"lwc-limepkg-scrive",{"platform":[16],"context":[16],"testing":[4],"testing2":[8,"testing-2"],"testing3":[1025,"testing-3"],"document":[32],"session":[32],"config":[32],"includePerson":[32],"includeCoworker":[32],"cloneDocument":[32],"isOpen":[32]}]]],["lwc-limepkg-scrive-loader",[[1,"lwc-limepkg-scrive-loader",{"platform":[16],"context":[16]}]]]], options);
  });
};

export { defineCustomElements };
