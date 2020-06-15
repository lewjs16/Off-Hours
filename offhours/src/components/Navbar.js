import React from 'react';
import { Nav, Navbar } from 'react-bootstrap';
import styled from 'styled-components';

const Styles = styled.div`
    .navbar {
        background-color: #222;
    }

    .navbar-brand, .navbar-nav .nav-link {
        color #bbb;

        &:hover {
            color: white;
        }
    }
`;

export const NavigationBar = () => (
    <Styles>
        <Navbar>
            <Navbar.Brand href="/"><img src={require("../img/assets/logo1.png")}></img>Offhours</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav"/>
            <Navbar.Collapse id="basic-nav">
                <Nav className="ml-auto" style={{margin: 'auto'}}>
                    <Nav.Item><Nav.Link href="/Watch">Watch</Nav.Link></Nav.Item>
                    <Nav.Item><Nav.Link href="/Stream">Stream</Nav.Link></Nav.Item>
                </Nav>
            </Navbar.Collapse>
        </Navbar>
    </Styles>
)