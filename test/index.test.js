// test/index.test.js   ‑‑ ESM + working mocks
import { jest } from '@jest/globals';

/* stub @actions/core before anyone imports it */
jest.unstable_mockModule('@actions/core', () => ({
  getInput: jest.fn(),
  setFailed: jest.fn()
}));

process.env.GITHUB_WORKSPACE = '';

/* load mocked core and code under test */
const core = await import('@actions/core');
import fs from 'node:fs';
const {
  make_dir_universal,
  check_for_exclude_dir,
  get_line_info,
  get_line_end
} = await import('../index.js');

/* reset after each test */
afterEach(() => {
  jest.clearAllMocks();
  jest.restoreAllMocks();
});

/* ─────────────────────────────────────────── tests */
describe('make_dir_universal', () => {
  it('converts backslashes', () => {
    expect(make_dir_universal('C:\\x\\y')).toBe('C:/x/y');
  });
  it('leaves forward slashes unchanged', () => {
    expect(make_dir_universal('/a/b')).toBe('/a/b');
  });
});

describe('check_for_exclude_dir', () => {
  it('true when exclude_dir empty', () =>
    expect(check_for_exclude_dir('/x', '')).toBe(true));
  it('false when path starts with excluded dir', () =>
    expect(check_for_exclude_dir('/x/y', '/x')).toBe(false));
  it('true when path outside excluded dir', () =>
    expect(check_for_exclude_dir('/x/y', '/z')).toBe(true));
});

describe('get_line_end', () => {
  beforeEach(() => core.getInput.mockReturnValue('10'));

  it('caps at start+numLines', () => {
    jest.spyOn(fs, 'readFileSync').mockReturnValue('\n'.repeat(50));
    expect(get_line_end('/f', 10)).toBe('20');
  });

  it('caps at file end', () => {
    jest.spyOn(fs, 'readFileSync').mockReturnValue('\n'.repeat(12));
    expect(get_line_end('/f', 10)).toBe('12');
  });
});

describe('get_line_info', () => {
  beforeEach(() => core.getInput.mockReturnValue('10'));

  it('GCC line parsing', () => {
    jest.spyOn(fs, 'readFileSync').mockReturnValue('\n'.repeat(123));
    expect(get_line_info('GCC', '/p.c:123: error: x'))
      .toEqual(['/p.c', '123', '123', 'error']);
  });

  it('Clang line parsing', () => {
    jest.spyOn(fs, 'readFileSync').mockReturnValue('\n'.repeat(127));
    expect(get_line_info('Clang', '/p.c:123: error: x'))
      .toEqual(['/p.c', '123', '127', 'error']);
  });

  it('MSVC line parsing', () => {
    jest.spyOn(fs, 'readFileSync').mockReturnValue('\n'.repeat(210));
    expect(get_line_info('MSVC', 'C:\\p.cpp(123): warning C420'))
      .toEqual(['C:\\p.cpp', '123', '133', 'warning']);
  });
});
