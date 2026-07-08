'use client';

import { Container, ContainerProps } from 'react-bootstrap';

export function AppContainer(props: ContainerProps) {
  return <Container fluid className="p-0" {...props} />;
}
