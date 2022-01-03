# labgrid-frontend-mle
A web frontend for labgrid in cooperation with MLE.

## Python Router

See [python-wamp-client](https://github.com/Simon-Deuring/labgrid-frontend-mle/tree/main/python-wamp-client) for further information.

## Web Client

### Development

Run `npm run start` to start a development server. Then navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

### Linting and Code Formatting

**Before creating a new pull request** you should run `npm run lint`. This triggers ESLint and Prettier and directly fixes all discovered problems. Additionally, every time a file is saved Prettier is called to guarantee high code quality.

### Building

Run `npm run build` to build the project. The build artifacts will be stored in the `dist/` directory.

### Running Unit Tests

Run `npm run test` to execute the unit tests via [Karma](https://karma-runner.github.io).

### Code Scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

### Further Help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.
