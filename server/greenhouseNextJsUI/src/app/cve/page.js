'use client';

import './_landing-page.scss';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

import {
  Grid,
  Column,
  Button,
  RadioButton,
  RadioButtonGroup,
} from '@carbon/react';

const config = require('../config/config.js');

import { IoRainyOutline } from 'react-icons/io5';
import Image from 'next/image';

const endpoints = require('../config/endpoints.js');

export default function Cve(CveParam) {
  const [lowTemp, setLowTemp] = useState('0');
  const [light, setlight] = useState('OFF');
  const [loading, setLoading] = useState(true);
  const [selectedEnv, setSelectedEnv] = useState(config.getEnv());
  const [error, setError] = useState();

  const setEnv = async (event) => {
    console.log('Event: ' + JSON.stringify(event));
    config.setEnv(event);
    setLoading(true);
    await getConfigData(event);
    setLoading(false);
  };

  const handleOnSubmit = (event) => {
    // Prevent default refresh
    event.preventDefault();

    writeConfig(event);
  };

  const writeConfig = (event) => {
    let configData = JSON.stringify({
      lightState: light,
      lightOnHH: '00:00',
      lightOffHH: '00:00',
    });

    console.log('Got: ' + JSON.stringify(configData));

    config.light(configData, selectedEnv);
  };

  const setRadioState = (state) => {
    let configData = JSON.stringify({
      lightState: state,
      lightOnHH: '00:00',
      lightOffHH: '00:00',
    });

    console.log('Got: ' + JSON.stringify(configData));

    config.light(configData, selectedEnv);

    setlight(state);
  };

  async function getConfigData(selectedEnv) {
    try {
      const configData = await config.getConfigData(selectedEnv);
      console.log('Config*******' + JSON.stringify(configData));
      if (configData) {
        setLowTemp(configData.temperatureRange[0]);
        setlight(configData.lightState);
      }
    } catch (err) {
      console.log(err);
      return <Grid className="config-page">Error</Grid>;
    }

    setLoading(false);
  }

  useEffect(() => {
    getConfigData(selectedEnv);
  }, []);

  if (loading) {
    return <Grid className="config-page">Loading</Grid>;
  }

  if (error) {
    return `Error! ${error}`;
  }

  var selectedRadio = 'radio-1';
  if (light === 'OFF') {
    selectedRadio = 'radio-2';
  }

  let lightButtonGroup = (
    <RadioButtonGroup
      defaultSelected={selectedRadio}
      legendText="CVE Scan"
      name="radio-button-default-group"
    >
      <RadioButton
        id="radio-1"
        labelText="On"
        value="radio-1"
        onClick={(e) => setRadioState('ON')}
      />
      <RadioButton
        id="radio-2"
        labelText="Off"
        value="radio-2"
        onClick={(e) => setRadioState('OFF')}
      />
    </RadioButtonGroup>
  );

  return (
    <Grid className="landing-page" fullWidth>
      <Column lg={16} md={8} sm={4} style={{ marginTop: '1px' }}>
        <hr
          style={{
            border: 'none',
            borderTop: '3px solid #797676',
            margin: '10px 0',
          }}
        />
      </Column>

      <Column lg={16} md={8} sm={4} style={{ marginTop: '4px' }}>
        <div style={{ width: '100%', height: 'auto', position: 'relative' }}>
          <Image
            alt="Watering Rules"
            src={'/cves.png'}
            width={1200}
            height={400}
            style={{ width: '100%', height: 'auto', objectFit: 'contain' }}
          />
          <div
            style={{
              position: 'absolute',
              top: '452px',
              right: '1380px',
              zIndex: 10,
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              padding: '8px 12px',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            {lightButtonGroup}
          </div>
        </div>
      </Column>
    </Grid>
  );
}
