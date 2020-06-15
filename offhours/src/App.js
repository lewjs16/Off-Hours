import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

import Watch  from './Watch';
import Browse  from './Browse';
import { Stream } from './Stream';
import { Layout } from './components/Layout';
import { NavigationBar } from './components/Navbar';


const App = () => {
    return (
      <div>
        <NavigationBar/>
        
        <Layout>
          <Router>
            <Switch>
              <Route exact path="/" component = {Browse} />
              <Route path="/watch/:id" component = {Watch} />
              <Route path="/stream/:id" component = {Stream} />
            </Switch>
          </Router>
        </Layout>
        </div>
    )
  }

export default App;
