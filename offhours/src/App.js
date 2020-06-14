import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'

import { Watch } from './Watch'
import { Stream } from './Stream'
import { Layout } from './components/Layout';
import { NavigationBar } from './components/Navbar'


class App extends Component {
  render() {
    return (
      <React.Fragment>

        <NavigationBar/>
        <Layout>
          <Router>
            <Switch>
              <Route exact path="/" component = {Watch} />
              <Route exact path="/watch" component = {Watch} />
              <Route exact path="/stream" component = {Stream} />
            </Switch>
          </Router>
        </Layout>

      </React.Fragment>
    );
  }
}

export default App;
